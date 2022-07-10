"""Module for processing of DTV details."""
import logging
import os
import re
import time
from typing import Literal

from lxml.etree import _ElementUnicodeResult
from lxml.html import HtmlElement, fromstring
from pandas import DataFrame, Series, read_parquet
from requests import Session, urllib3  # type:ignore

from stringprocessing import cleanevfromentry
thelogger: logging.Logger = logging.getLogger("TSH.resultParser")
PARQUETENGINE: Literal["fastparquet", "pyarrow", "auto"] = "fastparquet"
MYREGEX: Literal[r"(?P<Verein>.*)–(?P<Verband>.*)\((?P<ID>\d+)\)"] = r"(?P<Verein>.*)–(?P<Verband>.*)\((?P<ID>\d+)\)"
def create_dtv_df() -> DataFrame:
    """Build dataframe from all organisations taken from DTV-Website."""
    dtv_associations: DataFrame = DataFrame(
        columns=["ID", "Verband", "Verein", "Ort"]
    ).set_index("ID")
    # Maybe better create with <https://stackoverflow.com/a/72784123>
    # Or <https://numpy.org/doc/stable/user/basics.rec.html>?
    # np.dtype([('ID',int),('Verband','O'),('Verein','O'),('Ort','O')])
    # needs to be object type because of variable lenght
    testdtass = []
    dtv_associations: DataFrame = DataFrame(
        {
            "ID": Series(dtype="int"),
            "Verband": Series(dtype="str"),
            "Verein": Series(dtype="str"),
            "Ort": Series(dtype="str"),
        }
    ).set_index("ID")
    search_url = "https://www.tanzsport.de/de/service/vereinssuche"
    urllib3.disable_warnings()
    xpath_for_token = (
        '//*[@id="mod_vereinssuche_formular"]/input[@name="REQUEST_TOKEN"]/@value'
    )
    xpath_for_orgs = '//div[@id="service-vereinssuche"]//div[@class="result_body"]'
    with Session() as sess_context:
        sess_context.verify = False
        rqtoken: str = fromstring(sess_context.get(search_url).content).xpath(
            xpath_for_token
        )
        login_data: dict[str, str | int] = {
            "FORM_SUBMIT": "mod_vereinssuche_formular",
            "REQUEST_TOKEN": rqtoken,
            "name": "",
            "standort": "",
            "landesverband[]": "",
            "seite": 0,
        }
        tempfound: list[HtmlElement]
        while (
            tempfound := fromstring(
                sess_context.post(search_url, data=login_data).content
            )
            .xpath(xpath_for_orgs)[0]
            .getchildren()
        ):
            thelogger.debug(len(tempfound))
            for eintrag in tempfound:
                if eintrag.tag == "h3":  # Neue Ortsangabe
                    thelogger.debug("Neuer Ort: %s", eintrag.text)
                    the_place: str = eintrag.text
                else:  # Neuer Verein
                    # thelogger.debug("%s",repr(eintrag))
                    orgdata: list[_ElementUnicodeResult] = eintrag.xpath(
                        'div[@class="trigger"]/h3/text()'
                    )
                    # thelogger.debug("orgdata %s",orgdata[0])
                    if tempmatch := re.match(MYREGEX, orgdata[0]):
                        the_name, the_group, the_id = tempmatch.groups()
                        tempmatchdict: dict[str, str] = tempmatch.groupdict()
                        tempmatchdict["Ort"] = the_place
                        if the_group is not None:
                            testdtass.extend([tempmatchdict])
                            dtv_associations.loc[int(the_id)] = [
                                the_group.strip(),
                                cleanevfromentry(the_name),
                                the_place.strip(),
                            ]
            login_data["seite"] += 1
    #thelogger.info("WWWWWWWWWWWWWWWWWWWWWWWW %s", testdtass)
    testdtassdf:DataFrame=DataFrame(testdtass).set_index("ID")
    #.select_dtypes(['object']).apply(lambda x: x.str.strip())
    testdtassdf["Verein"]=testdtassdf["Verein"].apply(cleanevfromentry)
    testdtassdf[["Verband","Ort"]]=testdtassdf[["Verband","Ort"]].apply(str.strip)
    #thelogger.info("XXXXXXXXXXXXXXXXXXXXXXXXX %s", testdtassdf.sort_index())
    thelogger.debug("%s", dtv_associations.describe())
    thelogger.debug(
        "%s", dtv_associations[["Verband", "Verein"]].groupby("Verband").count()
    )
    thelogger.debug("%s", testdtassdf[["Verband", "Verein"]].groupby("Verband").count())
    return testdtassdf.sort_index()


def get_dtv_df(autoupdate: bool = True) -> DataFrame:
    """Retrieve dataframe of associations from Cache or Web."""
    dtv_associations_cache_file: str = (
        __file__[: __file__.rfind("/")] + "/dtv_associations.parquet"  # noqa: E203
    )
    max_cache_age_in_seconds = 7 * 24 * 60 * 60  # eine Woche
    if os.path.exists(dtv_associations_cache_file) and not (
        autoupdate
        and time.time() - os.path.getmtime(dtv_associations_cache_file)
        > max_cache_age_in_seconds
    ):  # Cache-Datei vorhanden
        thelogger.info(
            "DTV-Vereinsdaten sind vom %s.",
            time.ctime(os.path.getmtime(dtv_associations_cache_file)),
        )
        dtv_associations: DataFrame = read_parquet(
            dtv_associations_cache_file, engine=PARQUETENGINE
        )
    else:  # Keine Cache-Datei vorhanden
        thelogger.info("Aktuelle DTV-Vereinsdaten werden geholt.")
        dtv_associations: DataFrame = create_dtv_df()
        dtv_associations.to_parquet(dtv_associations_cache_file, engine=PARQUETENGINE)
        thelogger.info("DTV-Vereinsdaten aktualisiert.")
    return dtv_associations
