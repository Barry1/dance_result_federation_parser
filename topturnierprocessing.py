"""Module for TopTurnier-specific functions."""

import logging
from io import StringIO
from typing import Literal, cast
from urllib.error import HTTPError

from bs4 import BeautifulSoup
from bs4.element import ResultSet, SoupStrainer, Tag
from lxml.etree import _ElementTree as ElementTree
from pandas import DataFrame, concat, read_html
from requests import get as requests_get

from configprocessing import MyConfigT, readconfig, setuplogger
from dtvprocessing import get_dtv_df
from esvprocessing import get_couples_df
from stringprocessing import clean_number_from_couple, cleanevfromentry

thelogger: logging.Logger = setuplogger("Basti." + __name__)
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
    assert baseurlwith.endswith(
        ("index.htm", "index.html")
    ), 'URL muss auf "/" und index.htm[l] enden'
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
            tournmtsdict[eintrag.text] = f"{baseurl}/" + href_val
    return tournmtsdict


def tt_from_erg(theresulturl: str) -> DataFrame:
    """Process erg.html from TopTurnier resultpage."""
    assert theresulturl.endswith(
        "erg.htm"
    ), f"{theresulturl} endet nicht auf erg.htm"
    # requests-Rückmeldung mit .ok abfragen und if
    if (
        tempifinternal := requests_get(
            theresulturl,
            timeout=MY_TIMEOUT,
            headers={"User-agent": "Mozilla"},
        )
    ).ok:
        tab1tbl: list[DataFrame] = read_html(
            StringIO(tempifinternal.text.replace("<BR>", "</td><td>")),
            attrs={"class": "tab1"},
        )
    else:
        thelogger.debug(
            "HTTP-Fehler bei tab1tbl Nummer %s. Wenn es die %s-Datei nicht gibt, ist das Turnier evtl. ausgefallen?",
            tempifinternal.status_code,
            theresulturl,
        )
        return DataFrame(columns=["Platz", "Paar", "Verein", "Verband"])
    erg_df: DataFrame
    try:
        tab2tbl: list[DataFrame] = read_html(
            StringIO(
                requests_get(
                    theresulturl,
                    timeout=MY_TIMEOUT,
                    headers={"User-agent": "Mozilla"},
                ).text.replace("<BR>", "</td><td>")
            ),
            attrs={"class": "tab2"},
        )
    except ValueError:
        erg_df = concat(tab1tbl)
        # Zeilen mit ungültigen Plätzen, Namen, Vereinen löschen
        erg_df.dropna(axis=0, subset=erg_df.columns[:3], inplace=True)
        # Spalten mit ungültigen Einträgen (Wertungsteile) löschen
        erg_df.dropna(axis=1, inplace=True)
        erg_df = erg_df.iloc[:, [0, -2, -1]]
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
    erg_df.columns = ["Platz", "Paar", "Verein"]
    # Nur Zeilen behalten, bei denen ein "." im Platz ist
    erg_df = erg_df[["." in zeile for zeile in erg_df.Platz]]
    erg_df.loc[:, "Paar"] = erg_df.Paar.map(clean_number_from_couple)
    erg_df.loc[:, "Verein"] = erg_df.Verein.map(cleanevfromentry)
    # erg_df['ordercol']=erg_df['Platz'].apply(lambda x:int(x[:x.find('.')]))
    # erg_df=erg_df.sort_values(by='ordercol').drop('ordercol', axis=1)
    # "inner" ging, sortiere falsch#.sort_values(by="Platz")
    if _CFG_DICT["ESVCOUPLES"]:
        cpldf: DataFrame = get_couples_df()
        cpldf["Verband"] = "NAMEDCOUPLE"
        return erg_df.merge(cpldf, on="Paar", how="inner")
    return erg_df.merge(get_dtv_df(autoupdate=False), on="Verein", how="left")


def interpret_tt_result(theresulturl: str) -> DataFrame:
    """Process TopTurnier URL."""
    assert theresulturl.endswith("index.htm"), (
        "Es muss die index.htm-URL vom Turnier"
        "(nicht der Veranstaltung) angegeben werden"
    )
    thelogger.debug(theresulturl)
    theresulturl = theresulturl.replace("index.htm", "erg.htm")
    ret_df: DataFrame = DataFrame(
        columns=["Platz", "Paar", "Verein", "Verband", "Ort"]
    )
    try:
        ret_df = tt_from_erg(theresulturl)
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
    return ret_df
