"""Module for the presentation Layer of the results."""

import logging

# from pandas import DataFrame
from pandas import DataFrame

# from strictly_typed_pandas import DataSet as DataFrame
from valuefragments import eprint

from configprocessing import LOGGERNAME, MyConfigT

thelogger: logging.Logger = logging.getLogger(f"{LOGGERNAME}.{__name__}")


def print_joomla(
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
        #        "Die &Uuml;berschriften sind die Links zum Ergebnis.",
        "</p>",
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
        value.loc[value.Verband == "NAMEDCOUPLE", "Verband"] = cfg_dict["THEFEDERATION"]
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


def print_wordpress(
    wholereslink: str,
    allreslinks: list[str],
    tsh_results: list[DataFrame],
    compnames: list[str],
    cfg_dict: MyConfigT,
) -> None:
    """Export data as WordPress."""
    thelogger.debug("PresentationLayer WordPress")
    print(
        "<!-- wp:paragraph -->",
        "<p>Einleitende Worte.</p>",
        "<!-- /wp:paragraph -->",
        "<!-- wp:more -->",
        "<!--more-->",
        "<!-- /wp:more -->",
        "<!-- wp:paragraph -->",
        "<p>Hier folgend die Ergebnisse",
        "(nach Verf&uuml;gbarkeit fortlaufend gepflegt)",
        f"der {cfg_dict['THEFEDERATION']}-Paare.",
        "</p>",
        "<!-- /wp:paragraph -->",
    )
    for actreslink, value, turnier_info in zip(allreslinks, tsh_results, compnames):
        tournhdr: str = (
            (
                "<!-- wp:heading -->"
                f'<h2 class="wp-block-heading"><a href="{actreslink}" target="_blank" '
                f'rel="noopener">{turnier_info}</a></h2>'
                "<!-- /wp:heading -->"
            )
            if cfg_dict["HEADLINELINKS"]
            else (
                "<!-- wp:heading -->"
                f'<h2 class="wp-block-heading">{turnier_info}</h2>'
                "<!-- /wp:heading -->"
            )
        )
        # Falls die gefundenen Ergebnisse aus Paarnamen kommen,
        # wird der Verband künstlich gesetzt:
        # value.Verband[value.Verband == "NAMEDCOUPLE"]
        value.loc[value.Verband == "NAMEDCOUPLE", "Verband"] = cfg_dict["THEFEDERATION"]
        if value[value.Verband == cfg_dict["THEFEDERATION"]].empty:
            print("<!--")  # Beginning of Comment
            print(tournhdr)
            print(f"<p>Leider ohne {cfg_dict['THEFEDERATION']}-Beteiligung.</p>")
            print("-->")  # End of Comment
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
                print('<!-- wp:table {"hasFixedLayout":false} -->')
                print('<figure class="wp-block-table">')
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
                print("</tbody></table></figure>")
                print("<!-- /wp:table -->")
            else:
                print("<ul>")
                for resline in value[
                    value.Verband == cfg_dict["THEFEDERATION"]
                ].iterrows():
                    print(
                        f"<li>{resline[1].Platz}",
                        f"{resline[1].Paar} ({resline[1].Verein})</li>",
                        sep="",
                    )
                print("</ul>")
            print("<!-- wp:spacer -->")
            print(
                '<div style="height:100px" aria-hidden="true" class="wp-block-spacer"></div>'
            )
            print("<!-- /wp:spacer -->")
            print(
                '<!-- wp:separator {"className":"is-style-wide","backgroundColor":"white"} -->'
            )
            print(
                '<hr class="wp-block-separator has-text-color has-white-color has-alpha-channel-opacity has-white-background-color has-background is-style-wide"/>'
            )
            print("<!-- /wp:separator -->")
    print(
        "<!-- wp:paragraph -->",
        '<p>Das Gesamtergebnis ist unter dem <a href="',
        wholereslink,
        '" target="_blank">Link</a> zu finden.</p>',
        "<!-- /wp:paragraph -->",
        sep="",
    )
    print(
        "<!-- wp:paragraph -->",
        "<p>Falls ich ein Paar übersehen habe, ",
        "bitte ich freundlich um eine ",
        "<a href=",
        f'"mailto:{cfg_dict["INFORMEMAIL"]}?subject=&Uuml;bersehenes%20Ergebnis"',
        ">Email</a>.</p>",
        "<!-- /wp:paragraph -->",
        sep="",
    )


def presentation_function(
    wholereslink: str,
    allreslinks: list[str],
    tsh_results: list[DataFrame],
    compnames: list[str],
    cfg_dict: MyConfigT,
) -> None:
    """Returns result based on config selector."""
    match cfg_dict["RESULTFORMAT"]:
        case "JOOMLA":
            return print_joomla(
                wholereslink, allreslinks, tsh_results, compnames, cfg_dict
            )
        case "WORDPRESS" | "TSH":
            return print_wordpress(
                wholereslink, allreslinks, tsh_results, compnames, cfg_dict
            )
        case "MARKDOWN":
            return print_markdown(
                wholereslink, allreslinks, tsh_results, compnames, cfg_dict
            )
        case wrongresultformat:
            thelogger.debug(
                "Missing or invalid RESULTFORMAT '%s' in config",
                wrongresultformat,
            )
            return print_markdown(
                wholereslink, allreslinks, tsh_results, compnames, cfg_dict
            )
