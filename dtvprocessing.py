"""Module for processing of DTV details."""

import asyncio
import logging
import os
import re
import time
from typing import Literal, TypedDict

import aiofiles
import aiofiles.os

# from lxml.etree import _ElementUnicodeResult
from lxml.html import HtmlElement, fromstring
from pandas import DataFrame, read_parquet
from requests import Session, urllib3  # type:ignore

import sqlitedatabase
from configprocessing import setuplogger
from sqlitedatabase import insertnewclubs
from stringprocessing import cleanevfromentry

# from strictly_typed_pandas import DataSet as DataFrame


thelogger: logging.Logger = setuplogger()
MAX_CACHE_AGE_IN_SECONDS: int = 7 * 24 * 60 * 60  # eine Woche
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
    """Build dataframe from all organisations taken from DTV-Website."""
    # Maybe better create with <https://stackoverflow.com/a/72784123>
    # Or <https://numpy.org/doc/stable/user/basics.rec.html>?
    # np.dtype([('ID',int),('Verband','O'),('Verein','O'),('Ort','O')])
    # needs to be object type because of variable lenght
    urllib3.disable_warnings()
    with Session() as the_sess_context:
        # sess_context.verify = False
        dtv_assocs_dict_list: list[dict[str, str]] = parse_dtv_to_list_dict(
            sess_context=the_sess_context
        )
    return assocsdf_from_list_dict(input_list_dict=dtv_assocs_dict_list)


def assocsdf_from_list_dict(
    input_list_dict: list[dict[str, str]]
) -> DataFrame:
    """Convert assosiations list of dicts to DataFrame."""
    dtv_associations: DataFrame = DataFrame.from_records(
        data=input_list_dict, index="ID"
    )
    dtv_associations.index = dtv_associations.index.astype(dtype=int)
    dtv_associations["Verein"] = dtv_associations["Verein"].apply(
        func=cleanevfromentry
    )
    dtv_associations[["Verband", "Ort"]] = dtv_associations[
        ["Verband", "Ort"]
    ].apply(lambda x: x.str.strip())
    thelogger.info("%s", dtv_associations.describe())
    thelogger.debug(
        "%s",
        dtv_associations[["Verband", "Verein"]].groupby(by="Verband").count(),
    )
    return dtv_associations.sort_index()


def parse_dtv_to_list_dict(sess_context: Session) -> list[dict[str, str]]:
    """Parse DTV Homepage for associations, return aus list of dicts."""
    xpath_token: str = (
        '//*[@id="mod_vereinssuche_formular"]/'
        'input[@name="REQUEST_TOKEN"]/@value'
    )
    dtv_assocs_dict_list: list[dict[str, str]] = []
    rqtoken: str = fromstring(
        html=sess_context.get(url=SEARCH_URL).content
    ).xpath(xpath_token)
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
    allmatches: list[dict[str, str]] = list()
    tempfound: list[HtmlElement]
    thelogger.debug(
        "%s", sess_context.post(url=SEARCH_URL, data=login_data).content
    )
    while (
        tempfound := fromstring(
            html=sess_context.post(url=SEARCH_URL, data=login_data).content
        )
        .xpath(XPATH_FOR_ORGS)[0]
        .getchildren()
    ):
        thelogger.debug(msg=len(tempfound))
        the_place: str = ""
        # orgdata: list[_ElementUnicodeResult]
        for eintrag in tempfound:
            if eintrag.tag == "h3":  # Neue Ortsangabe
                if eintrag.text:
                    thelogger.debug("Neuer Ort: %s", eintrag.text)
                    the_place = eintrag.text
            else:  # Neuer Verein
                # thelogger.debug("%s",repr(eintrag))
                orgdata = eintrag.xpath(
                    _path='div[@class="trigger"]/h3/text()'
                )
                if tempmatch := re.match(MYREGEX, orgdata[0]):
                    tempmatchdict: dict[str, str] = tempmatch.groupdict()
                    tempmatchdict["Ort"] = the_place
                    # sqlitedatabase.insertnewclub(tempmatchdict)
                    allmatches.append(tempmatchdict)
                    dtv_assocs_dict_list.extend([tempmatchdict])
        login_data["seite"] += 1
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
        if not await aiofiles.os.path.isdir("associations"):
            await aiofiles.os.mkdir(path="associations")
        async with aiofiles.open(
            file=f"associations/{verbandsvereine[0]}.txt", mode="w"
        ) as ausgabedatei:
            await ausgabedatei.write(
                f"{len(verbandsvereine[1])} Vereine im {verbandsvereine[0]}:\n"
            )
            await ausgabedatei.write(
                verbandsvereine[1][["Verein", "Ort"]].to_string()
            )
            await ausgabedatei.write("\n")


if __name__ == "__main__":
    asyncio.run(main=outputassocfiles())
