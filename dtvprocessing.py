"""Module for processing of DTV details."""
import logging
import os
import re
import time
from typing import Literal, TypedDict

from lxml.etree import _ElementUnicodeResult
from lxml.html import HtmlElement, fromstring
from pandas import DataFrame, read_parquet
from requests import Session, urllib3  # type:ignore

from stringprocessing import cleanevfromentry

thelogger: logging.Logger = logging.getLogger("Basti.resultParser")
MAX_CACHE_AGE_IN_SECONDS = 7 * 24 * 60 * 60  # eine Woche
MYREGEX = r"(?P<Verein>.*)–(?P<Verband>.*)\((?P<ID>\d+)\)"
PARQUETENGINE: Literal["fastparquet", "pyarrow", "auto"] = "fastparquet"
SEARCH_URL = "https://www.tanzsport.de/de/service/vereinssuche"
XPATH_FOR_ORGS = '//div[@id="service-vereinssuche"]//div[@class="result_body"]'


def create_dtv_df() -> DataFrame:
    """Build dataframe from all organisations taken from DTV-Website."""
    # Maybe better create with <https://stackoverflow.com/a/72784123>
    # Or <https://numpy.org/doc/stable/user/basics.rec.html>?
    # np.dtype([('ID',int),('Verband','O'),('Verein','O'),('Ort','O')])
    # needs to be object type because of variable lenght
    dtv_assocs_dict_list: list[dict[str, str]] = []
    urllib3.disable_warnings()
    xpath_for_token = '//*[@id="mod_vereinssuche_formular"]/input[@name="REQUEST_TOKEN"]/@value'
    with Session() as sess_context:
        sess_context.verify = False
        rqtoken: str = fromstring(sess_context.get(SEARCH_URL).content).xpath(
            xpath_for_token
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
        tempfound: list[HtmlElement]
        while (
            tempfound := fromstring(
                sess_context.post(SEARCH_URL, data=login_data).content
            )
            .xpath(XPATH_FOR_ORGS)[0]
            .getchildren()
        ):
            thelogger.debug(len(tempfound))
            the_place: str = ""
            orgdata: list[_ElementUnicodeResult]
            for eintrag in tempfound:
                if eintrag.tag == "h3":  # Neue Ortsangabe
                    if eintrag.text:
                        thelogger.debug("Neuer Ort: %s", eintrag.text)
                        the_place = eintrag.text
                else:  # Neuer Verein
                    # thelogger.debug("%s",repr(eintrag))
                    orgdata = eintrag.xpath(
                        'div[@class="trigger"]/h3/text()'
                    )
                    if tempmatch := re.match(MYREGEX, orgdata[0]):
                        tempmatchdict: dict[str, str] = tempmatch.groupdict()
                        tempmatchdict["Ort"] = the_place
                        dtv_assocs_dict_list.extend([tempmatchdict])
            login_data["seite"] += 1
    dtv_associations: DataFrame = DataFrame.from_records(
        dtv_assocs_dict_list, index="ID"
    )
    dtv_associations.index = dtv_associations.index.astype(int)
    dtv_associations["Verein"] = dtv_associations["Verein"].apply(
        cleanevfromentry
    )
    dtv_associations[["Verband", "Ort"]] = dtv_associations[
        ["Verband", "Ort"]
    ].apply(lambda x: x.str.strip())
    thelogger.info("%s", dtv_associations.describe())
    thelogger.debug(
        "%s",
        dtv_associations[["Verband", "Verein"]].groupby("Verband").count(),
    )
    return dtv_associations.sort_index()


def get_dtv_df(autoupdate: bool = True) -> DataFrame:
    """Retrieve dataframe of associations from Cache or Web."""
    dtv_associations_cache_file: str = (
        __file__[: __file__.rfind("/")]
        + "/dtv_associations.parquet"  # noqa: E203
    )
    dtv_associations: DataFrame
    if os.path.exists(dtv_associations_cache_file) and not (
        autoupdate
        and time.time() - os.path.getmtime(dtv_associations_cache_file)
        > MAX_CACHE_AGE_IN_SECONDS
    ):  # Cache-Datei vorhanden
        thelogger.info(
            "DTV-Vereinsdaten sind vom %s.",
            time.ctime(os.path.getmtime(dtv_associations_cache_file)),
        )
        dtv_associations = read_parquet(
            dtv_associations_cache_file, engine=PARQUETENGINE
        )
    else:  # Keine oder veraltete Cache-Datei vorhanden
        thelogger.info("Aktuelle DTV-Vereinsdaten werden geholt.")
        dtv_associations = create_dtv_df()
        dtv_associations.to_parquet(
            dtv_associations_cache_file, engine=PARQUETENGINE
        )
        thelogger.info("DTV-Vereinsdaten aktualisiert.")
    return dtv_associations
