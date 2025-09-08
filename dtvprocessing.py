"""Module for processing of DTV details."""

import asyncio
import logging
import os
import time
from typing import Literal

import aiofiles
import aiofiles.os
from pandas import DataFrame, read_json, read_parquet

from configprocessing import setuplogger
from stringprocessing import cleanevfromentry

thelogger: logging.Logger = setuplogger()
MAX_CACHE_AGE_IN_SECONDS: int = 7 * 24 * 60 * 60 * 100  # einhundert Wochen
# leider hat der DTV die Vereinssuche umgebaut
# und die VereinsID kommt nicht mehr raus
MYREGEX: Literal["(?P<Verein>.*) – (?P<Verband>.*) \\((?P<ID>\\d+)\\)"] = (
    r"(?P<Verein>.*) – (?P<Verband>.*) \((?P<ID>\d+)\)"
)
PARQUETENGINE: Literal["fastparquet", "pyarrow", "auto"] = "fastparquet"
SEARCH_URL: Literal["https://www.tanzsport.de/de/service/vereinssuche"] = (
    "https://www.tanzsport.de/de/service/vereinssuche"
)
XPATH_FOR_ORGS: Literal[
    '//div[@id="container_grid"]//div[@class="result_body"]'
] = '//div[@id="container_grid"]//div[@class="result_body"]'


def create_dtv_df() -> DataFrame:
    """Build dataframe from all organisations taken from DTV.
    New method from 2025-09-07, parser no longer needed."""
    dtv_associations: DataFrame = read_json(
        "https://event.api.tanzsport.de/vereine", orient="records"
    ).set_index("nummer")
    dtv_associations.rename(
        columns={"city": "Ort", "name": "Verein", "federation": "Verband"},
        inplace=True,
    )
    dtv_associations["Verband"] = dtv_associations["Verband"].replace(
        to_replace={
            8: "(TAF)",
            1308: "HTV",
            1408: "HATV",
            1508: "Berlin",
            1608: "Bayern",
            1708: "Brandenburg",
            1808: "LTV Bremen",
            1908: "NTV",
            2008: "Saarland",
            2108: "TBW",
            2208: "TMV",
            2308: "TNW",
            2508: "TRP",
            2608: "TSH",
            2708: "Thüringen",
            2808: "Sachsen",
            2908: "Sachsen-Anhalt",
        }
    )
    dtv_associations["Verein"] = dtv_associations["Verein"].apply(
        func=cleanevfromentry
    )
    dtv_associations[["Ort"]] = dtv_associations[["Ort"]].apply(
        lambda x: x.str.strip()
    )
    dtv_associations.index = dtv_associations.index.astype(dtype=int)
    thelogger.info("%s", dtv_associations.describe())
    thelogger.debug(
        "%s",
        dtv_associations[["Verband", "Verein"]].groupby(by="Verband").count(),
    )
    thelogger.debug("%s", dtv_associations.loc[404])
    # sqlitedatabase  insertnewclubs(allmatches) - war bei alter API
    return dtv_associations.sort_index()


def parse_dtv_to_list_dict(sess_context: Session) -> list[dict[str, str]]:
    """Parse DTV Homepage for associations, return aus list of dicts."""
    xpath_token: str = (
        '//*[@id="mod_vereinssuche_formular"]/'
        'input[@name="REQUEST_TOKEN"]/@value'
    )
    dtv_assocs_dict_list: list[dict[str, str]] = []
    rqtoken: str = fromstring(sess_context.get(url=SEARCH_URL).content).xpath(
        xpath_token
    )
    login_data_type = TypedDict(
        "login_data_type",
        {
            "FORM_SUBMIT": str,
            "REQUEST_TOKEN": str,
            "name": str,
            "standort": str,
            "landesverband[]": str,
            "seite": int,
        },
    )
    login_data: login_data_type = {
        "FORM_SUBMIT": "mod_vereinssuche_formular",
        "REQUEST_TOKEN": rqtoken,
        "name": "",
        "standort": "",
        "landesverband[]": "",
        "seite": 0,
    }
    # proposed from CircleCI instead of list()
    allmatches: list[dict[str, str]] = []
    tempfound: list[HtmlElement]
    thelogger.debug(
        "%s", sess_context.post(url=SEARCH_URL, data=login_data).content
    )
    while (
        tempfound := fromstring(
            sess_context.post(url=SEARCH_URL, data=login_data).content
        )
        .xpath(XPATH_FOR_ORGS)[0]
        .getchildren()
    ):
        thelogger.debug(msg=len(tempfound))
        the_place: str = ""
        for eintrag in tempfound:
            if eintrag.tag == "h3":  # Neue Ortsangabe
                if eintrag.text:
                    thelogger.debug("Neuer Ort: %s", eintrag.text)
                    the_place = eintrag.text
            elif tempmatch := re.match(
                MYREGEX,
                eintrag.xpath(_path='div[@class="trigger"]/h3/text()')[0],
            ):
                tempmatchdict: dict[str, str] = tempmatch.groupdict()
                tempmatchdict["Ort"] = the_place
                tempmatchdict["Verein"] = cleanevfromentry(
                    tempmatchdict["Verein"]
                )
                # sqlitedatabase.insertnewclub(tempmatchdict)
                allmatches.append(tempmatchdict)
                dtv_assocs_dict_list.extend([tempmatchdict])
        login_data["seite"] += 1
    if not os.getenv("CI"):
        # only outside of CI-Workflow like github action
        # <https://stackoverflow.com/a/73973555>
        insertnewclubs(allmatches)
    return dtv_assocs_dict_list


def get_dtv_df(autoupdate: bool = True) -> DataFrame:
    """Retrieve dataframe of associations from Cache or Web."""
    dtv_associations_cache_file: str = (
        f"{__file__[:__file__.rfind(os.sep)]}/dtv_associations.parquet"
    )
    dtv_associations: DataFrame
    if os.path.exists(dtv_associations_cache_file) and not (
        autoupdate
        and time.time()
        - os.path.getmtime(filename=dtv_associations_cache_file)
        > MAX_CACHE_AGE_IN_SECONDS
    ):  # Cache-Datei vorhanden
        thelogger.info(
            "DTV-Vereinsdaten sind vom %s.",
            time.ctime(os.path.getmtime(filename=dtv_associations_cache_file)),
        )
        dtv_associations = read_parquet(
            path=dtv_associations_cache_file, engine=PARQUETENGINE
        )
    else:  # Keine oder veraltete Cache-Datei vorhanden
        thelogger.info(msg="Aktuelle DTV-Vereinsdaten werden geholt.")
        dtv_associations = create_dtv_df()
        dtv_associations.to_parquet(
            path=dtv_associations_cache_file, engine=PARQUETENGINE
        )
        thelogger.info(msg="DTV-Vereinsdaten aktualisiert.")
    return dtv_associations


async def outputassocfiles() -> None:
    """Write file for each association."""
    dtv_assocs_df: DataFrame = get_dtv_df()
    print(
        dtv_assocs_df.pivot_table(
            index="Verband", values="Verein", aggfunc="count"
        )
    )
    print(dtv_assocs_df[dtv_assocs_df.Verband == "TSH"])
    for verbandsvereine in dtv_assocs_df.groupby(by="Verband"):
        # make folder associations if needed
        verbandsname: str = str(verbandsvereine[0])
        #        verbandsname: str = (
        #            verbandsvereine[0].decode()
        #            if isinstance(verbandsvereine[0], bytes)
        #            else verbandsvereine[0]
        #        )
        if not await aiofiles.os.path.isdir("associations"):
            await aiofiles.os.mkdir(path="associations")
        async with aiofiles.open(
            file=f"associations/{verbandsname}.txt",
            mode="w",
        ) as ausgabedatei:
            await ausgabedatei.write(
                f"{len(verbandsvereine[1])} Vereine im {verbandsname}:\n"
            )
            await ausgabedatei.write(
                verbandsvereine[1][["Verein", "Ort"]].to_string()
            )
            await ausgabedatei.write("\n")


if __name__ == "__main__":
    asyncio.run(main=outputassocfiles())
