#!/usr/bin/env -S /usr/bin/time --format "\tDauer %e [s] \t%U [s] User-Zeit\t%S [s] System-Zeit\t%P CPU" python3 -OO
# coding=utf-8
"""Turnier-Ergebnis-Parser
urllib.request für https nötig
https://www.w3schools.com/xml/xpath_syntax.asp
"""
import asyncio
from typing import Callable, cast
from urllib.error import HTTPError
from urllib.request import urlopen

from joblib import Parallel, delayed
from lxml.html import parse
from pandas import DataFrame
from pandas import set_option as pandas_set_option
from valuefragments import ic

from dtvprocessing import get_dtv_df
from topturnierprocessing import checkttontree, interpret_tt_result, srparserurl
from tpsprocessing import checktpsontree, interpret_tps_result, ogparserurl

RUN_ASYNC = True
pandas_set_option("mode.chained_assignment", "raise")  # warn,raise,None


async def async_eventurl_to_web(eventurl: str) -> None:
    """Async convert URL from Event to HTML for TSH CMS."""
    try:
        with urlopen(eventurl) as openedurl:
            tree = await asyncio.to_thread(parse, openedurl)
    except HTTPError as http_error:
        print(http_error)
    else:
        theparsefun: Callable[[str], dict[str, str]]
        the_interpret_fun: Callable[[str], DataFrame]
        if checktpsontree(tree):
            ic(f"{eventurl} ist eine TPS-Veranstaltung")
            theparsefun = ogparserurl
            the_interpret_fun = interpret_tps_result
        elif checkttontree(tree):
            ic(f"{eventurl} ist eine TT-Veranstaltung")
            theparsefun = srparserurl
            the_interpret_fun = interpret_tt_result
        else:
            print(f"Die URL {eventurl} kann weder TPS noch TT zugeordnet werden.")
            return
        allreslinks = theparsefun(eventurl).values()
        tsh_results: list[DataFrame] = list(
            await asyncio.gather(
                *(
                    asyncio.to_thread(the_interpret_fun, a)
                    for a in theparsefun(eventurl).values()
                )
            )
        )
        print_tsh_web(list(allreslinks), tsh_results)


def eventurl_to_web(eventurl: str) -> None:
    """Convert URL from Event to HTML for TSH CMS."""
    try:
        with urlopen(eventurl) as openedurl:
            tree = parse(openedurl)
    except HTTPError as http_error:
        print(http_error)
    else:
        theparsefun: Callable[[str], dict[str, str]]
        the_interpret_fun: Callable[[str], DataFrame]
        if checktpsontree(tree):
            ic(f"{eventurl} ist eine TPS-Veranstaltung")
            theparsefun = ogparserurl
            the_interpret_fun = interpret_tps_result
        elif checkttontree(tree):
            ic(f"{eventurl} ist eine TT-Veranstaltung")
            theparsefun = srparserurl
            the_interpret_fun = interpret_tt_result
        else:
            print(f"Die URL {eventurl} kann weder TPS noch TT zugeordnet werden.")
            return
        allreslinks = theparsefun(eventurl).values()
        tsh_results: list[DataFrame] = cast(
            list[DataFrame],
            Parallel(n_jobs=1 if __debug__ else -1, verbose=10 if __debug__ else 0)(
                delayed(the_interpret_fun)(a) for a in theparsefun(eventurl).values()
            ),
        )
        print_tsh_web(list(allreslinks), tsh_results)


def print_tsh_web(allreslinks: list[str], tsh_results: list[DataFrame]) -> None:
    """Export data as HTML for TSH-CMS."""
    print(
        "<p>Einleitende Worte.</p>",
        '<hr id="system-readmore" />',
        "<p>Noch mehr einleitende Worte.</p>",
        "<!-- ===================================================== -->",
    )
    for actreslink, value in zip(allreslinks, tsh_results):
        lastpos = actreslink.rfind("/")  # type: int
        turnier_info = actreslink[
            actreslink.rfind("/", 0, lastpos) + 1 : lastpos
        ]  # type: str
        print(
            '<h1><a href="'
            + actreslink
            + '" target="_blank" rel="noopener">'
            + turnier_info
            + "</a></h1>"
        )
        if value[value.Verband == "TSH"].empty:
            print("<p>Leider ohne TSH-Beteiligung.</p>")
        else:
            print(
                '<div style="float: right; margin-left: 10px;'
                ' text-align: center;font-size: 8pt;">'
            )
            print(
                '<img src="https://loremflickr.com/150/200/ballroom-dancing"'
                ' alt="Beispielfoto" height="200" />'
            )
            print("<br />Foto: loremflickr.com</div>")
            print("<ul>")
            for resline in value[value.Verband == "TSH"].iterrows():
                # display(resline)
                # display(resline[1])
                print(
                    "<li>"
                    + resline[1].Platz
                    + " "
                    + resline[1].Paar
                    + " ("
                    + resline[1].Verein
                    + ")</li>"
                )
            print("</ul>")
        print("<!-- ===================================================== -->")


if __name__ == "__main__":
    # execute only if run as a script
    import sys

    if len(sys.argv) > 1:
        for theurl in sys.argv[1:]:
            print(f"Auswertung von {theurl}")
            if RUN_ASYNC:
                asyncio.run(async_eventurl_to_web(theurl))
            else:
                eventurl_to_web(theurl)
    else:
        print("Selbsttest des Moduls resultParser")
        print(get_dtv_df().loc[403:406])
        urlszumpruefen = [
            "http://tsa.de.cool/20190914_Senioren/index.htm",
            "http://www.tanzen-in-sh.de/ergebnisse/2019/2019-02-02_GLM_Kin-Jug_D-A_LAT/index.htm",
            "http://blauesband-berlin.de/Ergebnisse/2019/blauesband2019/index.htm",
            "http://www.ergebnisse-tanzsport-glinde.de/mediapool/Turniere-2019/2019.09.28%20GLM",
            "http://tsk-buchholz.de/images/Tanzclub/Sparten/Turniertanz/GLM%202020.02.29",
        ]
        for theurl in urlszumpruefen:
            print(f"Geprüft wird die Funktion anhand von {theurl}")
            if RUN_ASYNC:
                asyncio.run(async_eventurl_to_web(theurl))
            else:
                eventurl_to_web(theurl)
