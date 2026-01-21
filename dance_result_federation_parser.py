#!/usr/bin/env -S /usr/bin/time python3 -OO
# --format "\tDauer %e [s] \t%U [s] User-Zeit\t%S [s] System-Zeit\t%P CPU"
# coding=utf-8
"""Turnier-Ergebnis-Parser
urllib.request für https nötig
https://www.w3schools.com/xml/xpath_syntax.asp
"""

import asyncio
import logging
from functools import partial
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from joblib import Parallel, delayed

# noinspection PyProtectedMember
from lxml.etree import _ElementTree

# import lxml.etree
from lxml.html import parse
from pandas import DataFrame
from pandas import set_option as pandas_set_option

# from strictly_typed_pandas import DataSet as DataFrame
from valuefragments import run_grouped

from configprocessing import MyConfigT, readconfig, setuplogger
from dtvprocessing import get_dtv_df
from presentationlayer import presentation_function
from stringprocessing import og_human_comp_info, sr_human_comp_info
from topturnierprocessing import (
    checkttontree,
    interpret_tt_result,
    srparserurl,
)
from tpsprocessing import checktpsontree, interpret_tps_result, ogparserurl

thelogger: logging.Logger = setuplogger()
_CFG_DICT: MyConfigT = readconfig()
pandas_set_option("mode.chained_assignment", "raise")  # warn,raise,None
# pandas_set_option("mode.copy_on_write", True)


def reslinks_interpreter(
    tree: _ElementTree,
) -> tuple[
    Callable[[str], dict[str, str]],
    Callable[[str], DataFrame],
    Callable[[str], str],
]:
    """Handle difference of TT and TPS."""
    if checktpsontree(tree):
        thelogger.info("Es ist eine TPS-Veranstaltung")
        return ogparserurl, interpret_tps_result, og_human_comp_info
    if checkttontree(tree):
        thelogger.info("Es ist eine TT-Veranstaltung")
        return srparserurl, interpret_tt_result, sr_human_comp_info
    thelogger.debug("Die URL kann weder TPS noch TT zugeordnet werden.")
    raise NotImplementedError("Don't know how to parse.")


async def async_eventurl_to_web(eventurl: str) -> None:
    """Async convert URL from Event to HTML for TSH CMS."""
    thelogger.info("Verarbeite %s", eventurl)
    try:
        openedurl = urlopen(eventurl)  # nosec B310
        thelogger.debug("%s wurde geöffnet", eventurl)
    except URLError as url_error:  # spricht der Server kein https?
        thelogger.exception(
            "Die URL %s ist nicht erreichbar, "
            "möglicherweise spricht der Server kein https?",
            eventurl,
        )
        thelogger.exception(url_error)
        eventurl = eventurl[:4] + eventurl[5:]
        thelogger.debug(
            "Die URL %s wurde auf http umgestellt, "
            "möglicherweise ist sie jetzt erreichbar.",
            eventurl,
        )
        thelogger.info("Versuche %s zu öffnen.", eventurl)
        openedurl = urlopen(eventurl)  # nosec B310
        thelogger.debug("%s wurde geöffnet.", eventurl)
    thelogger.info("Die URL %s ist erreichbar.", eventurl)
    try:
        with openedurl:
            eventurl = openedurl.geturl()
            tree: _ElementTree = await asyncio.to_thread(parse, openedurl)
    except HTTPError as http_error:
        thelogger.exception(http_error)
    else:
        try:
            theparsefun: Callable[[str], dict[str, str]]
            the_interpret_fun: Callable[[str], DataFrame]
            human_comp_info: Callable[[str], str]
            (
                theparsefun,
                the_interpret_fun,
                human_comp_info,
            ) = reslinks_interpreter(tree)
        except NotImplementedError:
            thelogger.exception(
                "%s kann nicht verarbeitet werden: Weder TT noch TPS.",
                eventurl,
            )
        else:
            allreslinks = theparsefun(eventurl).values()
            compnames: list[str] = [
                human_comp_info(lnk) for lnk in allreslinks
            ]
            tsh_results: list[DataFrame]
            # <https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.run_in_executor>
            # python >=3.11 TaskGroup instead of gather
            # <https://docs.python.org/3/library/asyncio-task.html#asyncio.TaskGroup>
            if _CFG_DICT["TOTHREAD"]:
                tsh_results = await run_grouped(
                    [
                        partial(the_interpret_fun, onelink)
                        for onelink in allreslinks
                    ],
                    "thread",
                )
            else:
                tsh_results = await run_grouped(
                    [
                        partial(the_interpret_fun, onelink)
                        for onelink in allreslinks
                    ],
                    "tpe",
                )
            presentation_function(
                eventurl, list(allreslinks), tsh_results, compnames, _CFG_DICT
            )


def eventurl_to_web(synceventurl: str) -> None:
    """Convert URL from Event to HTML for TSH CMS."""
    try:
        with urlopen(synceventurl) as openedurl:  # nosec B310
            synceventurl = openedurl.geturl()
            tree: _ElementTree = parse(openedurl)
    except HTTPError as sync_http_error:
        thelogger.exception(sync_http_error)
    else:
        try:
            human_comp_info: Callable[[str], str]
            the_interpret_fun: Callable[[str], DataFrame]
            theparsefun: Callable[[str], dict[str, str]]
            (
                theparsefun,
                the_interpret_fun,
                human_comp_info,
            ) = reslinks_interpreter(tree)
        except NotImplementedError:
            thelogger.exception(
                "%s kann nicht verarbeitet werden: Weder TT noch TPS.",
                synceventurl,
            )
        else:
            allreslinks = theparsefun(synceventurl).values()
            compnames: list[str] = [
                human_comp_info(thelink) for thelink in allreslinks
            ]
            tsh_results: list[DataFrame] = Parallel(
                n_jobs=1 if __debug__ else -1,
                verbose=10 if __debug__ else 0,
                backend="multiprocessing",
                # Testrun multiprocessing 2.899999998509884 (25,661 für 5)
                # Testrun threading 4.420000001788139 (29,347 für 5)
                # Testrun loky 4.8099999986588955 (30,918 für 5)
                #                    prefer='processes',
            )(delayed(the_interpret_fun)(a) for a in allreslinks)
            presentation_function(
                synceventurl,
                list(allreslinks),
                tsh_results,
                compnames,
                _CFG_DICT,
            )


__all__: list[str] = ["interpret_tt_result", "presentation_function"]
if __name__ == "__main__":
    # execute only if run as a script
    if _CFG_DICT["PYANNOTATE"]:
        from pyannotate_runtime import collect_types

        collect_types.init_types_collection()
        collect_types.start()
        # Besonders nötig, damit bei ASYNC nur einmal
    # ggf. die DTV-Vereinliste aktualisiert wird
    _: DataFrame = get_dtv_df().sort_index()
    #    _: DataFrame = get_dtv_df().loc[403:406]
    # vielleicht auch mit
    # <https://docs.python.org/3/library/asyncio-sync.html>
    # zu lösen
    if len(theargv := __import__("sys").argv) > 1:
        for theurl in theargv[1:]:
            thelogger.info("Auswertung von %s", theurl)
            if _CFG_DICT["RUN_ASYNC"]:
                asyncio.run(async_eventurl_to_web(theurl), debug=__debug__)
            else:
                eventurl_to_web(theurl)
    else:
        thelogger.info("Selbsttest des Moduls resultParser")
        thelogger.info(get_dtv_df().sort_index().loc[403:406])
        for theurl in _CFG_DICT["CHECKINGURLS"]:
            thelogger.info("Geprüft wird die Funktion anhand von %s", theurl)
            if _CFG_DICT["RUN_ASYNC"]:
                asyncio.run(async_eventurl_to_web(theurl), debug=__debug__)
            else:
                eventurl_to_web(theurl)
    if _CFG_DICT["PYANNOTATE"]:
        collect_types.stop()
        collect_types.dump_stats("type_info.json")
