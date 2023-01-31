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
from typing import Callable, Literal, cast
from urllib.error import HTTPError
from urllib.request import urlopen

from joblib import Parallel, delayed
from lxml.etree import _ElementTree
from lxml.html import parse
from pandas import DataFrame
from pandas import set_option as pandas_set_option
from valuefragments import eprint, run_grouped_in_tpe

from dtvprocessing import get_dtv_df
from stringprocessing import og_human_comp_info, sr_human_comp_info
from topturnierprocessing import (
    checkttontree,
    interpret_tt_result,
    srparserurl,
)
from tpsprocessing import checktpsontree, interpret_tps_result, ogparserurl

thefederation: Literal[
    "TSH",
    "HATV",
    "TBW",
    "HTV",
    "Bayern",
    "Berlin",
    "Bremen",
    "NTV",
    "TNW",
    "TRP",
    "SLT",
    "LTV Br",
    "TMV",
    "TVS",
    "TVSA",
    "TTSV",
] = "TSH"
PYANNOTATE: Literal[True, False] = False
RUN_ASYNC: Literal[True, False] = True
TOTHREAD: Literal[True, False] = False
HEADLINELINKS: Literal[True, False] = False
URLSZUMPRUEFEN: list[str] = [
    "http://tsa.de.cool/20190914_Senioren/index.htm",
    "http://www.tanzen-in-sh.de/ergebnisse/2019/2019-02-02_GLM_Kin-Jug_D-A_LAT/index.htm",
    "http://blauesband-berlin.de/Ergebnisse/2019/blauesband2019/index.htm",
    "http://www.ergebnisse-tanzsport-glinde.de/mediapool/Turniere-2019/2019.09.28%20GLM",
    "http://tsk-buchholz.de/images/Tanzclub/Sparten/Turniertanz/GLM%202020.02.29",
]
thelogger: logging.Logger = logging.getLogger("Basti.resultParser")
logformatter: logging.Formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)  # https://docs.python.org/3/library/logging.html#logrecord-attributes
logfilehandler: logging.FileHandler = logging.FileHandler("resultParser.log")
logfilehandler.setFormatter(logformatter)
thelogger.addHandler(logfilehandler)
if __debug__:
    thelogger.setLevel(logging.DEBUG)
else:
    thelogger.setLevel(logging.INFO)
IMG_PREP: bool = False
pandas_set_option("mode.chained_assignment", "raise")  # warn,raise,None


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
    try:
        with urlopen(eventurl) as openedurl:
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
            if TOTHREAD:
                # type: ignore[attr-defined]
                async with asyncio.TaskGroup() as my_task_group:
                    tsh_results_tasks: list[asyncio.Task[DataFrame]] = [
                        my_task_group.create_task(
                            asyncio.to_thread(the_interpret_fun, onelink)
                        )
                        for onelink in allreslinks
                    ]
                tsh_results = [
                    ready_task.result() for ready_task in tsh_results_tasks
                ]
            else:
                tsh_results = await run_grouped_in_tpe(
                    [partial(the_interpret_fun, a) for a in allreslinks]
                )
            print_tsh_web(eventurl, list(allreslinks), tsh_results, compnames)


def eventurl_to_web(synceventurl: str) -> None:
    """Convert URL from Event to HTML for TSH CMS."""
    try:
        with urlopen(synceventurl) as openedurl:
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
            tsh_results: list[DataFrame] = cast(
                list[DataFrame],
                Parallel(
                    n_jobs=1 if __debug__ else -1,
                    verbose=10 if __debug__ else 0,
                    backend="multiprocessing",
                    # Testrun multiprocessing 2.899999998509884 (25,661 für 5)
                    # Testrun threading 4.420000001788139 (29,347 für 5)
                    # Testrun loky 4.8099999986588955 (30,918 für 5)
                    #                    prefer='processes',
                )(delayed(the_interpret_fun)(a) for a in allreslinks),
            )
            print_tsh_web(
                synceventurl, list(allreslinks), tsh_results, compnames
            )


def print_tsh_web(
    wholereslink: str,
    allreslinks: list[str],
    tsh_results: list[DataFrame],
    compnames: list[str],
) -> None:
    """Export data as HTML for TSH-CMS."""
    print(
        "<p>Einleitende Worte.</p>",
        '<hr id="system-readmore" />',
        "<p>Hier folgend die Ergebnisse",
        "(nach Verf&uuml;gbarkeit fortlaufend gepflegt)",
        "der TSH-Paare.",
        #        "Die &Uuml;berschriften sind die Links zum Ergebnis.</p>",
        "<!-- =================================================== -->",
    )
    for actreslink, value, turnier_info in zip(
        allreslinks, tsh_results, compnames
    ):
        tournhdr: str = (
            (
                f'<h2><a href="{actreslink}" target="_blank" '
                f'rel="noopener">{turnier_info}</a></h2>'
            )
            if HEADLINELINKS
            else f"<h2>{turnier_info}</h2>"
        )
        if value[value.Verband == thefederation].empty:
            eprint(tournhdr)
            eprint("<p>Leider ohne TSH-Beteiligung.</p>")
            eprint(
                "<!-- =================================================== -->"
            )
        else:
            print(tournhdr)
            if IMG_PREP:
                print(
                    '<div style="float: right; margin-left: 10px;'
                    ' text-align: center;font-size: 8pt;">'
                )
                print(
                    "<img"
                    ' src="https://loremflickr.com/150/200/ballroom-dancing"'
                    ' alt="Beispielfoto" height="200" />'
                )
                print("<br />Foto: loremflickr.com</div>")
            print("<ul>")
            for resline in value[value.Verband == thefederation].iterrows():
                # display(resline)
                # display(resline[1])
                print(
                    f"<li>{resline[1].Platz}"
                    f"{resline[1].Paar} ({resline[1].Verein})</li>"
                )
            print("</ul>")
            print(
                "<!-- =================================================== -->"
            )
    print(
        '<p>Das Gesamtergebnis ist unter dem <a href="',
        wholereslink,
        '" target="_blank">Link</a> zu finden.</p>',
        sep="",
    )
    print(
        "<p>Falls ich ein Paar übersehen habe,",
        "bitte ich freundlich um eine",
        "<a href=",
        '"mailto:ebeling@tanzen-in-sh.de?subject=&Uuml;bersehenes%20Ergebnis"',
        ">Email</a>.</p>",
        sep="",
    )


__all__: list[str] = ["interpret_tt_result", "print_tsh_web"]
if __name__ == "__main__":
    # execute only if run as a script
    if PYANNOTATE:
        from pyannotate_runtime import collect_types

        collect_types.init_types_collection()
        collect_types.start()
    import sys

    # Besonders nötig, damit bei ASYNC nur einmal
    # ggf. die DTV-Vereinliste aktualisiert wird
    _: DataFrame = get_dtv_df().loc[403:406]
    #
    if len(sys.argv) > 1:
        for theurl in sys.argv[1:]:
            thelogger.info("Auswertung von %s", theurl)
            if RUN_ASYNC:
                asyncio.run(async_eventurl_to_web(theurl))
            else:
                eventurl_to_web(theurl)
    else:
        thelogger.info("Selbsttest des Moduls resultParser")
        thelogger.info(get_dtv_df().loc[403:406])
        for theurl in URLSZUMPRUEFEN:
            thelogger.info("Geprüft wird die Funktion anhand von %s", theurl)
            if RUN_ASYNC:
                asyncio.run(async_eventurl_to_web(theurl))
            else:
                eventurl_to_web(theurl)
    if PYANNOTATE:
        collect_types.stop()
        collect_types.dump_stats("type_info.json")
