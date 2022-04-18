"""Module for processing of DTV details."""
import os
import re
import time

from lxml.html import fromstring
from pandas import DataFrame, read_parquet
from requests import Session, urllib3  # type:ignore
from valuefragments import ic

from stringprocessing import cleanevfromentry

PARQUETENGINE = "fastparquet"  # the others seem not to work engine{‘auto’, ‘pyarrow’, ‘’}, default ‘auto’


def create_dtv_df() -> DataFrame:
    """Build dataframe from all organisations taken from DTV-Website."""
    dtv_associations = DataFrame(columns=["ID", "Verband", "Verein", "Ort"]).set_index(
        "ID"
    )
    search_url = "https://www.tanzsport.de/de/service/vereinssuche"
    urllib3.disable_warnings()
    xpath_for_token = (
        '//*[@id="mod_vereinssuche_formular"]/input[@name="REQUEST_TOKEN"]/@value'
    )
    xpath_for_orgs = '//div[@id="service-vereinssuche"]//div[@class="result_body"]'
    with Session() as sess_context:
        sess_context.verify = False
        rqtoken = fromstring(sess_context.get(search_url).content).xpath(
            xpath_for_token
        )
        login_data = {
            "FORM_SUBMIT": "mod_vereinssuche_formular",
            "REQUEST_TOKEN": rqtoken,
            "name": "",
            "standort": "",
            "landesverband[]": "",
            "seite": 0,
        }
        while (
            tempfound := fromstring(
                sess_context.post(search_url, data=login_data).content
            )
            .xpath(xpath_for_orgs)[0]
            .getchildren()
        ):
            # ic(len(tempfound))
            for eintrag in tempfound:
                if eintrag.tag == "h3":  # Neue Ortsangabe
                    # ic("Neuer Ort: " + eintrag.text)
                    the_place = eintrag.text
                else:  # Neuer Verein
                    # ic(tostring(eintrag))
                    orgdata = eintrag.xpath('div[@class="trigger"]/h3/text()')
                    if tempmatch := re.match(r"(.*)–(.*)\((\d+)\)", orgdata[0]):
                        the_group: str
                        the_name, the_group, the_id = tempmatch.groups()
                        if the_group is not None:
                            dtv_associations.loc[int(the_id)] = [
                                the_group.strip(),
                                cleanevfromentry(the_name),
                                the_place.strip(),
                            ]
            login_data["seite"] += 1
    ic(dtv_associations.describe())
    ic(dtv_associations[["Verband", "Verein"]].groupby("Verband").count())
    return dtv_associations.sort_index()


def get_dtv_df(autoupdate: bool = True) -> DataFrame:
    """Retrieve dataframe of associations from Cache or Web."""
    dtv_associations_cache_file = (
        __file__[: __file__.rfind("/")] + "/dtv_associations.parquet"  # noqa: E203
    )
    max_cache_age_in_seconds = 7 * 24 * 60 * 60  # eine Woche
    if os.path.exists(dtv_associations_cache_file) and not (
        autoupdate
        and time.time() - os.path.getmtime(dtv_associations_cache_file)
        > max_cache_age_in_seconds
    ):  # Cache-Datei vorhanden
        ic(
            "DTV-Vereinsdaten sind vom",
            time.ctime(os.path.getmtime(dtv_associations_cache_file)),
            ".",
        )
        dtv_associations = read_parquet(
            dtv_associations_cache_file, engine=PARQUETENGINE
        )
    else:  # Keine Cache-Datei vorhanden
        ic("Aktuelle DTV-Vereinsdaten werden geholt.")
        dtv_associations = create_dtv_df()
        dtv_associations.to_parquet(dtv_associations_cache_file, engine=PARQUETENGINE)
        ic("DTV-Vereinsdaten aktualisiert.")
    return dtv_associations
