"""Module for TopTurnier-specific functions."""

import logging
from io import StringIO
from os import getenv
from re import DOTALL, IGNORECASE, match
from typing import Literal, cast
from urllib.error import HTTPError

from bs4 import BeautifulSoup, ResultSet, Tag
from bs4.filter import SoupStrainer
from lxml.etree import _ElementTree as ElementTree
from pandas import DataFrame, concat, read_html
from requests import Response
from requests import get as requests_get

from configprocessing import LOGGERNAME, MyConfigT, readconfig
from dtvprocessing import get_dtv_df
from esvprocessing import get_couples_df
from sqlitedatabase import couple_club_federation, insertcouplestodb
from stringprocessing import clean_number_from_couple, cleanevfromentry

# from strictly_typed_pandas import DataSet as DataFrame


thelogger: logging.Logger = logging.getLogger(f"{LOGGERNAME}.{__name__}")
_CFG_DICT: MyConfigT = readconfig()
MY_TIMEOUT: Literal[3] = 3


def checkttontree(the_e_tree: ElementTree) -> bool:
    """Sucht in einem lxml-Tree nach Hinweisen dafür,
    ob das eine HTML-Seite von TopTurnier von Stefan Rath ist.
    Konkret wird nach einem Link auf die Homepage topturnier.de gesucht.
    Da die Schreibweise TopTurnier auch gefunden werden soll und lower-case
    nicht mit lxml funktioniert (XPATH2.0-Funktion) wird
    mit translate gearbeitet.
    """
    return bool(
        the_e_tree.xpath(
            "//meta[contains(translate(@content,"
            '"ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ",'
            '"abcdefghijklmnopqrstuvwxyzäöü"),"topturnier")]'
        )
    )


def srparserurl(baseurlwith: str) -> dict[str, str]:
    """Parse S. Rath TopTurnier URL.

    Basiert auf BeautifulSoup,
    benötigt für eine exemplarische Seite
    http://tsa.de.cool/20190914_Senioren 196 ms.
    """
    baseurl: str = baseurlwith[: baseurlwith.rfind("/")]
    tournmtsdict: dict[str, str] = {}
    for eintrag in cast(
        ResultSet[Tag],
        BeautifulSoup(
            requests_get(
                baseurlwith,
                timeout=MY_TIMEOUT,
                headers={"User-agent": "Mozilla"},
            ).text,
            features="lxml",
            parse_only=SoupStrainer("a"),
        )("span"),
    ):
        if (the_parent := eintrag.parent) is not None and not isinstance(
            href_val := the_parent["href"], list
        ):
            tournmtsdict[eintrag.text] = f"{baseurl}/{href_val}"
    return tournmtsdict


def tt_trndmntdatefrom(reqget: Response) -> dict[str, str]:
    """Use the Get-Response from erg.htm to get the date."""
    titledate = r".*<title>(?P<TAG>.*?)[./](?P<MONAT>.*?)[./](?P<JAHR>.*?) "
    if match_return := match(titledate, reqget.text, DOTALL | IGNORECASE):
        return match_return.groupdict()
    return {}


def tt_from_erg(theresultresponse: Response) -> DataFrame:
    """Process erg.html from TopTurnier resultpage - as request-Response"""
    try:
        tab1tbl: list[DataFrame] = read_html(
            StringIO(theresultresponse.text.replace("<BR>", "</td><td>")),
            attrs={"class": "tab1"},
        )
    except ValueError:
        thelogger.debug(
            "HTTP-Fehler bei tab1tbl Nummer %s."
            " Wenn es die %s-Datei nicht gibt,"
            " ist das Turnier evtl. ausgefallen?",
            theresultresponse.status_code,
            theresultresponse,
        )
        return DataFrame(columns=["Platz", "Paar", "Verein", "Verband"])
    erg_df: DataFrame
    try:
        tab2tbl: list[DataFrame] = read_html(
            StringIO(theresultresponse.text.replace("<BR>", "</td><td>")),
            flavor="lxml",
            attrs={"class": "tab2"},
        )
    except ValueError:
        erg_df = concat(tab1tbl)
        # Zeilen mit ungültigen Plätzen, Namen, Vereinen löschen
        erg_df.dropna(axis=0, subset=erg_df.columns[:3], inplace=True)
        # Spalten mit ungültigen Einträgen (Wertungsteile) löschen
        erg_df.dropna(axis=1, inplace=True)
        erg_df = erg_df.iloc[:, [0, -2, -1]]
        thelogger.debug("Within ValueError %s", "Zeile 106")
        thelogger.debug("%s", theresultresponse.text)
    except Exception as e:
        thelogger.error("An error occurred: %s", e)
        thelogger.error(
            "%s in line %i of %s",
            type(e).__name__,
            e.__traceback__.tb_lineno if e.__traceback__ else 0,
            __file__,
        )
        raise e
    else:
        erg_df = concat([*tab1tbl, *tab2tbl])
        # Zeilen mit ungültigen Plätzen, Namen, Vereinen löschen
        erg_df.dropna(axis=0, subset=erg_df.columns[:3], inplace=True)
        # Spalten mit ungültigen Einträgen (Wertungsteile) löschen
        erg_df.dropna(axis=1, inplace=True)
        if len(erg_df.columns) == 2:
            # Solisten haben keine Vereine
            erg_df["Verein"] = "∅"
        erg_df = erg_df.iloc[:, [0, 1, 2]]
    erg_df = erg_df.set_axis(["Platz", "Paar", "Verein"], axis="columns", copy=False)

    # Nur Zeilen behalten, bei denen ein "." im Platz ist
    erg_df = erg_df[["." in zeile for zeile in erg_df.Platz]]
    erg_df.loc[:, "Paar"] = erg_df.Paar.map(clean_number_from_couple)
    erg_df.loc[:, "Verein"] = erg_df.Verein.map(cleanevfromentry)
    cpldf: DataFrame
    if (ergdfgeridxs := erg_df.Verein == "Germany").any():
        # international competition, no club name
        erg_df = erg_df[ergdfgeridxs]
        cpldf = couple_club_federation()
        erg_df.rename(columns={"Verein": "Land"}, inplace=True)
        cpldf.rename(columns={"Name": "Verein"}, inplace=True)
        return erg_df.merge(cpldf, on="Paar", how="inner")

    # thelogger.debug("%s", erg_df)
    # erg_df['ordercol']=erg_df['Platz'].apply(lambda x:int(x[:x.find('.')]))
    # erg_df=erg_df.sort_values(by='ordercol').drop('ordercol', axis=1)
    # "inner" ging, sortiere falsch#.sort_values(by="Platz")
    #    if (geridxs:=erg_df.Verein=="Germany").sum()>0:
    #        thelogger.info("Germany %i",geridxs.sum())
    if _CFG_DICT["ESVCOUPLES"]:
        cpldf = get_couples_df()
        cpldf["Verband"] = "NAMEDCOUPLE"
        return erg_df.merge(cpldf, on="Paar", how="inner")
    return erg_df.merge(get_dtv_df(autoupdate=False), on="Verein", how="left")


def interpret_tt_result(theresulturl: str) -> DataFrame:
    """Process TopTurnier URL."""
    thelogger.debug("interpret_tt_result Aufruf mit %s", theresulturl)
    if not theresulturl.endswith("index.htm"):
        thelogger.debug("URL endet nicht auf index.htm")
        theresulturl += "/index.htm" if theresulturl.endswith("/") else "/index.htm"
    theresulturl = theresulturl.replace("index.htm", "erg.htm")
    thelogger.debug("interpret_tt_result Auswertung von %s", theresulturl)
    ret_df = DataFrame(columns=["Platz", "Paar", "Verein", "Verband"])
    ergurlresponse: Response = requests_get(
        theresulturl, timeout=MY_TIMEOUT, headers={"User-agent": "Mozilla"}
    )
    # thelogger.debug("hier %s",ergurlresponse)
    if ergurlresponse.ok:
        thedatedict: dict[str, str] = tt_trndmntdatefrom(ergurlresponse)
        thelogger.debug("Veranstaltungsdatum %s", thedatedict)
        monthtonum: dict[str, str] = {
            "Jan": "01",
            "Feb": "02",
            "Mar": "03",
            "Apr": "04",
            "May": "05",
            "Jun": "06",
            "Jul": "07",
            "Aug": "08",
            "Sep": "09",
            "Oct": "10",
            "Nov": "11",
            "Dec": "12",
        }
        tournamentdate: str = (
            thedatedict["JAHR"]
            + "-"
            + (
                thedatedict["MONAT"]
                if thedatedict["MONAT"].isdecimal()
                else monthtonum[thedatedict["MONAT"]]
            )
            + "-"
            + thedatedict["TAG"]
        )
        thelogger.info("Veranstaltungsdatum %s", tournamentdate)
        try:
            ret_df = tt_from_erg(ergurlresponse)
            # ret_df = tt_from_erg_url(theresulturl)
        except HTTPError as http_error:
            thelogger.warning(
                "Beim tt_from_erg von %s trat der HTTPError %s auf",
                theresulturl,
                http_error,
            )
        except ValueError as value_error:
            thelogger.debug(
                "Beim tt_from_erg von %s trat der ValueError %s auf",
                theresulturl,
                value_error,
            )
        except Exception as general_exception:
            thelogger.exception(
                "Beim tt_from_erg von %s trat %s auf",
                theresulturl,
                general_exception,
            )
            raise
        if not getenv("CI"):
            insertcouplestodb(ret_df, tournamentdate)
    thelogger.debug("%s", ret_df)
    return ret_df
