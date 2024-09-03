"""Module for the presentation Layer of the results."""

import logging

# from pandas import DataFrame
from pandas import DataFrame

# from strictly_typed_pandas import DataSet as DataFrame
from valuefragments import eprint

from configprocessing import LOGGERNAME, MyConfigT

thelogger: logging.Logger = logging.getLogger(f"{LOGGERNAME}.{__name__}")


def print_tsh_web(
    wholereslink: str,
    allreslinks: list[str],
    tsh_results: list[DataFrame],
    compnames: list[str],
    cfg_dict: MyConfigT,
) -> None:
    """Export data as HTML for TSH-CMS."""
    thelogger.debug("PresentationLayer for TSH-CMS")
    print(
        "<p>Einleitende Worte.</p>",
        '<hr id="system-readmore" />',
        "<p>Hier folgend die Ergebnisse",
        "(nach Verf&uuml;gbarkeit fortlaufend gepflegt)",
        f"der {cfg_dict['THEFEDERATION']}-Paare.",
        #        "Die &Uuml;berschriften sind die Links zum Ergebnis.</p>",
        "<!-- =================================================== -->",
    )
    for actreslink, value, turnier_info in zip(allreslinks, tsh_results, compnames):
        tournhdr: str = (
            (
                f'<h2><a href="{actreslink}" target="_blank" '
                f'rel="noopener">{turnier_info}</a></h2>'
            )
            if cfg_dict["HEADLINELINKS"]
            else f"<h2>{turnier_info}</h2>"
        )
        # Falls die gefundenen Ergebnisse aus Paarnamen kommen,
        # wird der Verband künstlich gesetzt:
        # value.Verband[value.Verband == "NAMEDCOUPLE"]
        try:
            value.loc[value.Verband == "NAMEDCOUPLE", "Verband"] = cfg_dict[
                "THEFEDERATION"
            ]
        except NotImplementedError as nie:
            eprint(
                f"HIER {__file__} muss Basti noch etwas tun @TODO inplace DataSet geht nicht."
            )
            eprint("error: ", nie)
            if nie.__traceback__:
                eprint("error file info: ", nie.__traceback__.tb_frame)
                eprint("error line#: ", nie.__traceback__.tb_lineno)
        if value[value.Verband == cfg_dict["THEFEDERATION"]].empty:
            print("<!--")  # Beginning of Comment
            print(tournhdr)
            print(f"<p>Leider ohne {cfg_dict['THEFEDERATION']}-Beteiligung.</p>")
            print("-->")  # End of Comment
            print("<!-- =================================================== -->")
        else:
            print(tournhdr)
            if cfg_dict["IMG_PREP"]:
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
            if cfg_dict["RESULTTABLE"]:
                print("<table>")
                print(
                    "<thead><tr><th>&nbsp;</th>",
                    '<th style="text-align: right;">Platz</th>',
                    '<th style="text-align: right;">Paar</th>',
                    '<th style="text-align: right;">Verein</th>',
                    "</tr></thead><tbody>",
                    sep="",
                )
                for resline in value[
                    value.Verband == cfg_dict["THEFEDERATION"]
                ].iterrows():
                    print(
                        "<tr><td><strong>&nbsp;</strong></td>",
                        '<td style="text-align: right;">',
                        resline[1].Platz,
                        '</td><td style="text-align: right;">',
                        resline[1].Paar,
                        '</td><td style="text-align: right;">',
                        resline[1].Verein,
                        "</td></tr>",
                        sep="",
                    )
                print("</tbody></table>")
            else:
                print("<ul>")
                for resline in value[
                    value.Verband == cfg_dict["THEFEDERATION"]
                ].iterrows():
                    # display(resline)
                    # display(resline[1])
                    print(
                        f"<li>{resline[1].Platz}",
                        f"{resline[1].Paar} ({resline[1].Verein})</li>",
                        sep="",
                    )
                print("</ul>")
            print("<!-- =================================================== -->")
    print(
        '<p>Das Gesamtergebnis ist unter dem <a href="',
        wholereslink,
        '" target="_blank">Link</a> zu finden.</p>',
        sep="",
    )
    print(
        "<p>Falls ich ein Paar übersehen habe, ",
        "bitte ich freundlich um eine ",
        "<a href=",
        f'"mailto:{cfg_dict["INFORMEMAIL"]}?subject=&Uuml;bersehenes%20Ergebnis"',
        ">Email</a>.</p>",
        sep="",
    )


def print_markdown(
    wholereslink: str,
    allreslinks: list[str],
    tsh_results: list[DataFrame],
    compnames: list[str],
    cfg_dict: MyConfigT,
) -> None:
    """Export data as Markdown."""
    thelogger.debug("PresentationLayer Markdown")
    print(
        "Die folgenden Inhalte sind die Auswertung der [Turnierergebnisse](",
        wholereslink,
        ") für den Verband ",
        cfg_dict["THEFEDERATION"],
        ".",
        sep="",
    )
    print(
        "Hier folgend die Ergebnisse (nach Verfügbarkeit fortlaufend gepflegt) ",
        f"der {cfg_dict['THEFEDERATION']}-Paare.",
        sep="",
    )
    for actreslink, value, turnier_info in zip(allreslinks, tsh_results, compnames):
        tournhdr: str = (
            "\n"
            + (
                f"## [{turnier_info}]({actreslink})"
                if cfg_dict["HEADLINELINKS"]
                else f"## {turnier_info}"
            )
            + "\n"
        )
        value.loc[value.Verband == "NAMEDCOUPLE", "Verband"] = cfg_dict["THEFEDERATION"]
        if value[value.Verband == cfg_dict["THEFEDERATION"]].empty:
            eprint(tournhdr)
            eprint(f"<p>Leider ohne {cfg_dict['THEFEDERATION']}-Beteiligung.</p>")
            eprint("<!-- =================================================== -->")
        else:
            print(tournhdr)
            if cfg_dict["IMG_PREP"]:
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
            if cfg_dict["RESULTTABLE"]:
                print("|Platz|Paar|Verein|")
                print("|---:|---:|---:|")
                for resline in value[
                    value.Verband == cfg_dict["THEFEDERATION"]
                ].iterrows():
                    print(f"|{resline[1].Platz}|{resline[1].Paar}|{resline[1].Verein}|")
            else:
                for resline in value[
                    value.Verband == cfg_dict["THEFEDERATION"]
                ].iterrows():
                    print(
                        f" - {resline[1].Platz} {resline[1].Paar} ({resline[1].Verein}"
                    )
    print(
        "\n",
        "Das Gesamtergebnis ist unter dem [Link](",
        wholereslink,
        "}) zu finden.",
        sep="",
    )
    print(
        "Falls ich ein Paar übersehen habe, bitte ich freundlich um eine ",
        f'[Email](mailto:{cfg_dict["INFORMEMAIL"]}?subject=&Uuml;bersehenes%20Ergebnis)"',
        sep="",
    )
