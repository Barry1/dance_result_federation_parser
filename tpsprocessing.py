"""Module for TPS-specific functions."""

import logging

# from __future__ import annotations
from urllib.parse import quote
from urllib.request import urlopen

# noinspection PyProtectedMember
from lxml.etree import _ElementTree
from lxml.html import parse
from pandas import DataFrame, read_html, to_numeric  # , option_context

from configprocessing import LOGGERNAME
from dtvprocessing import get_dtv_df
from stringprocessing import cleanevfromentry  # ,clean_number_from_couple

# from strictly_typed_pandas import DataSet as DataFrame


thelogger: logging.Logger = logging.getLogger(f"{LOGGERNAME}.{__name__}")


def checktpsontree(the_e_tree: _ElementTree) -> bool:
    """Search lxml-Tree for indicator if TPS."""
    return bool(
        the_e_tree.xpath(
            "//a[starts-with(translate(text(),"
            '"ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ",'
            '"abcdefghijklmnopqrstuvwxyzäöü"),"tps.net")]'
        )
    )


def ogparserurl(baseurl: str) -> dict[str, str]:
    """Parse results from O. Gröhns competition software."""
    tournmtsdict: dict[str, str] = {}
    base: str = baseurl[: baseurl.rfind("/")]
    with urlopen(baseurl) as urlrequest:  # nosec B310
        for entry in parse(urlrequest).xpath("/html/body/div/main/a[*]"):
            tournmtsdict[entry.xpath("div/div/h4/text()")[0]] = (
                f'{base}/{quote(entry.xpath("@href")[0])}'
            )
    if not tournmtsdict:  # keine in Main gefunden, jetzt DropDown nutzen
        for entry in parse(baseurl).xpath(
            "/html/body/nav/div[2]/ul/li[1]/ul/li[*]/a"
        ):
            tournmtsdict[entry.text] = f'{base}/{quote(entry.get("href"))}'
    return tournmtsdict


def interpret_tps_result(theresulturl: str) -> DataFrame:
    """Extract results from tps-made result-website."""
    assert theresulturl.endswith("index.html"), (  # nosec B101
        "Es muss die index.html-URL vom Turnier"
        " (nicht der Veranstaltung) angegeben werden"
    )
    theresulturl = theresulturl.replace("index.html", "result.html")
    thelogger.debug("Verarbeitung von %s", theresulturl)
    tps_result_df: DataFrame
    try:
        tps_result_df = read_html(
            theresulturl, attrs={"class": "table fa-lg"}
        )[0]
    except IndexError as index_error:
        thelogger.exception(
            "Bei interpret_tps_result von %s trag der IndexError %s auf.",
            theresulturl,
            index_error,
        )
        tps_result_df = DataFrame(
            columns=["Platz", "Startnummer", "Paar", "Verein"]
        )
    #    tps_result_df.columns = ["Platz", "Startnummer", "Paar", "Verein"]
    # tps_result_df = tps_result_df.set_axis(["Platz", "Startnummer", "Paar", "Verein"], axis="columns", copy=False)
    tps_result_df = tps_result_df.set_axis(
        labels=["Platz", "Startnummer", "Paar", "Verein"], axis="columns"
    )
    tps_result_df = tps_result_df[
        to_numeric(tps_result_df.Startnummer, errors="coerce").notnull()
    ]
    # with option_context("mode.chained_assignment", None):
    tps_result_df.loc[:, "Verein"] = tps_result_df.Verein.map(cleanevfromentry)
    # Sortierung korrigert
    return tps_result_df.merge(
        get_dtv_df(autoupdate=False), on="Verein", how="left"
    )
