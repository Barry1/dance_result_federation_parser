"""Module for the presentation Layer of the results."""

from contextlib import nullcontext
from io import TextIOWrapper
import logging
from collections.abc import Hashable, Iterator
from pandas import DataFrame, Series
from valuefragments import eprint
from configprocessing import LOGGERNAME, AppConfig

thelogger: logging.Logger = logging.getLogger(f"{LOGGERNAME}.{__name__}")


def print_ul_html(
    therowiterator: Iterator[tuple[Hashable, Series]],
    filehandle: TextIOWrapper | None,
) -> None:
    """Small printer for result ul."""
    # Usually it gets called with iterrows from a DataFrame
    print("<ul>", file=filehandle)
    for resline in therowiterator:
        print(
            f"<li>{resline[1].Platz}",
            f"{resline[1].Paar} ({resline[1].Verein})</li>",
            sep="",
            file=filehandle,
        )
    print("</ul>", file=filehandle)


def print_img_placeholder(
    filehandle: TextIOWrapper | None,
) -> None:
    """Small printer for example images."""
    print(
        '<div style="float: right; margin-left: 10px;'
        ' text-align: center;font-size: 8pt;">',
        file=filehandle,
    )
    print(
        "<img"
        ' src="https://loremflickr.com/150/200/ballroom-dancing"'
        ' alt="Beispielfoto" height="200" />',
        file=filehandle,
    )
    print("<br />Foto: loremflickr.com</div>", file=filehandle)


def print_joomla(
    wholereslink: str,
    allreslinks: list[str],
    tsh_results: list[DataFrame],
    compnames: list[str],
    cfg_dict: AppConfig,
) -> None:
    """Export data as HTML for TSH-CMS."""
    thelogger.debug("PresentationLayer for TSH-CMS")
    with (
        open(cfg_dict.OUTPUT, "w", encoding="utf-8")
        if cfg_dict.OUTPUT
        else nullcontext() as filehandle
    ):
        print(
            "<p>Einleitende Worte.</p>",
            '<hr id="system-readmore" />',
            "<p>Hier folgend die Ergebnisse",
            "(nach Verf&uuml;gbarkeit fortlaufend gepflegt)",
            f"der {cfg_dict.THEFEDERATION}-Paare.",
            #        "Die &Uuml;berschriften sind die Links zum Ergebnis.",
            "</p>",
            "<!-- =================================================== -->",
            file=filehandle,
        )
        for actreslink, value, turnier_info in zip(
            allreslinks, tsh_results, compnames
        ):
            tournhdr: str = (
                (
                    f'<h2><a href="{actreslink}" target="_blank" '
                    f'rel="noopener">{turnier_info}</a></h2>'
                )
                if cfg_dict.HEADLINELINKS
                else f"<h2>{turnier_info}</h2>"
            )
            # Falls die gefundenen Ergebnisse aus Paarnamen kommen,
            # wird der Verband künstlich gesetzt:
            # value.Verband[value.Verband == "NAMEDCOUPLE"]
            value.loc[value.Verband == "NAMEDCOUPLE", "Verband"] = (
                cfg_dict.THEFEDERATION
            )
            if value[value.Verband == cfg_dict.THEFEDERATION].empty:
                print("<!--", file=filehandle)  # Beginning of Comment
                print(tournhdr, file=filehandle)
                print(
                    f"<p>Leider ohne {cfg_dict.THEFEDERATION}-Beteiligung.</p>",
                    file=filehandle,
                )
                print("-->", file=filehandle)  # End of Comment
            else:
                print(tournhdr, file=filehandle)
                if cfg_dict.IMG_PREP:
                    print_img_placeholder(filehandle=filehandle)
                if cfg_dict.RESULTTABLE:
                    print("<table>", file=filehandle)
                    print(
                        "<thead><tr><th>&nbsp;</th>",
                        '<th style="text-align: right;">Platz</th>',
                        '<th style="text-align: right;">Paar</th>',
                        '<th style="text-align: right;">Verein</th>',
                        "</tr></thead><tbody>",
                        sep="",
                        file=filehandle,
                    )
                    for resline in value[
                        value.Verband == cfg_dict.THEFEDERATION
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
                            file=filehandle,
                        )
                    print("</tbody></table>", file=filehandle)
                else:
                    print_ul_html(
                        therowiterator=value[
                            value.Verband == cfg_dict.THEFEDERATION
                        ].iterrows(),
                        filehandle=filehandle,
                    )
            print(
                "<!-- =================================================== -->",
                file=filehandle,
            )
        print(
            '<p>Das Gesamtergebnis ist unter dem <a href="',
            wholereslink,
            '" target="_blank">Link</a> zu finden.</p>',
            sep="",
            file=filehandle,
        )
        print(
            "<p>Falls ich ein Paar übersehen habe, ",
            "bitte ich freundlich um eine ",
            '<a href="mailto:',
            cfg_dict.INFORMEMAIL,
            '?subject=&Uuml;bersehenes%20Ergebnis"',
            ">Email</a>.</p>",
            sep="",
            file=filehandle,
        )


def print_markdown(
    wholereslink: str,
    allreslinks: list[str],
    tsh_results: list[DataFrame],
    compnames: list[str],
    cfg_dict: AppConfig,
) -> None:
    """Export data as Markdown."""
    thelogger.debug("PresentationLayer Markdown")
    with (
        open(cfg_dict.OUTPUT, "w", encoding="utf-8")
        if cfg_dict.OUTPUT
        else nullcontext() as filehandle
    ):
        print(
            "Die folgenden Inhalte sind die Auswertung der [Turnierergebnisse](",
            wholereslink,
            ") für den Verband ",
            cfg_dict.THEFEDERATION,
            ".",
            sep="",
            file=filehandle,
        )
        print(
            "Hier folgend die Ergebnisse ",
            "(nach Verfügbarkeit fortlaufend gepflegt) ",
            f"der {cfg_dict.THEFEDERATION}-Paare.",
            sep="",
            file=filehandle,
        )
        for actreslink, value, turnier_info in zip(
            allreslinks, tsh_results, compnames
        ):
            tournhdr: str = (
                "\n"
                + (
                    f"## [{turnier_info}]({actreslink})"
                    if cfg_dict.HEADLINELINKS
                    else f"## {turnier_info}"
                )
                + "\n"
            )
            value.loc[value.Verband == "NAMEDCOUPLE", "Verband"] = (
                cfg_dict.THEFEDERATION
            )
            if value[value.Verband == cfg_dict.THEFEDERATION].empty:
                eprint(tournhdr)
                eprint(
                    f"<p>Leider ohne {cfg_dict.THEFEDERATION}-Beteiligung.</p>",
                )
                eprint(
                    "<!-- =================================================== -->"
                )
            else:
                print(tournhdr, file=filehandle)
                if cfg_dict.IMG_PREP:
                    print_img_placeholder(filehandle=filehandle)
                if cfg_dict.RESULTTABLE:
                    print("|Platz|Paar|Verein|", file=filehandle)
                    print("|---:|---:|---:|", file=filehandle)
                    for resline in value[
                        value.Verband == cfg_dict.THEFEDERATION
                    ].iterrows():
                        print(
                            "|",
                            resline[1].Platz,
                            "|",
                            resline[1].Paar,
                            "|",
                            resline[1].Verein,
                            "|",
                            sep="",
                            file=filehandle,
                        )
                else:
                    for resline in value[
                        value.Verband == cfg_dict.THEFEDERATION
                    ].iterrows():
                        print(
                            "- ",
                            resline[1].Platz,
                            " ",
                            resline[1].Paar,
                            " (",
                            resline[1].Verein,
                            ")",
                            sep="",
                            file=filehandle,
                        )
        print(
            "\n",
            "Das Gesamtergebnis ist unter dem [Link](",
            wholereslink,
            ") zu finden.",
            sep="",
            file=filehandle,
        )
        print(
            "Falls ich ein Paar übersehen habe, bitte ich freundlich um eine ",
            "[Email](mailto:",
            cfg_dict.INFORMEMAIL,
            "?subject=&Uuml;bersehenes%20Ergebnis).",
            sep="",
            file=filehandle,
        )


def print_wordpress(
    wholereslink: str,
    allreslinks: list[str],
    tsh_results: list[DataFrame],
    compnames: list[str],
    cfg_dict: AppConfig,
) -> None:
    """Export data as WordPress."""
    thelogger.debug("PresentationLayer WordPress")
    with (
        open(cfg_dict.OUTPUT, "w", encoding="utf-8")
        if cfg_dict.OUTPUT
        else nullcontext() as filehandle
    ):
        print(
            "<!-- wp:paragraph -->",
            "<p>Einleitende Worte.</p>",
            "<!-- /wp:paragraph -->",
            file=filehandle,
        )
        print(
            "<!-- wp:more -->",
            "<!--more-->",
            "<!-- /wp:more -->",
            file=filehandle,
        )
        print(
            "<!-- wp:paragraph -->",
            "<p>Hier folgend die Ergebnisse",
            "(nach Verf&uuml;gbarkeit fortlaufend gepflegt)",
            f"der {cfg_dict.THEFEDERATION}-Paare.",
            "</p>",
            "<!-- /wp:paragraph -->",
            file=filehandle,
        )
        for actreslink, value, turnier_info in zip(
            allreslinks, tsh_results, compnames
        ):
            tournhdr: str = (
                (
                    "<!-- wp:heading -->"
                    '<h2 class="wp-block-heading">'
                    f'<a href="{actreslink}" target="_blank" '
                    f'rel="noopener">{turnier_info}</a></h2>'
                    "<!-- /wp:heading -->"
                )
                if cfg_dict.HEADLINELINKS
                else (
                    "<!-- wp:heading -->"
                    f'<h2 class="wp-block-heading">{turnier_info}</h2>'
                    "<!-- /wp:heading -->"
                )
            )
            # Falls die gefundenen Ergebnisse aus Paarnamen kommen,
            # wird der Verband künstlich gesetzt:
            # value.Verband[value.Verband == "NAMEDCOUPLE"]
            value.loc[value.Verband == "NAMEDCOUPLE", "Verband"] = (
                cfg_dict.THEFEDERATION
            )
            if not value[value.Verband == cfg_dict.THEFEDERATION].empty:
                print(tournhdr, file=filehandle)
                if cfg_dict.IMG_PREP:
                    print(
                        '<!-- wp:image {"sizeSlug":"large"} -->',
                        file=filehandle,
                    )
                    print(
                        '<figure class="wp-block-image size-large">',
                        file=filehandle,
                    )
                    print(
                        "<img"
                        ' src="https://loremflickr.com/150/200/ballroom-dancing"'
                        ' alt="Beispielfoto" />',
                        file=filehandle,
                    )
                    print(
                        '<figcaption class="wp-element-caption">'
                        "Foto: loremflickr.com</figcaption>",
                        file=filehandle,
                    )
                    print("</figure>", file=filehandle)
                    print("<!-- /wp:image -->", file=filehandle)
                if cfg_dict.RESULTTABLE:
                    print(
                        '<!-- wp:table {"hasFixedLayout":false} -->',
                        file=filehandle,
                    )
                    print('<figure class="wp-block-table">', file=filehandle)
                    print("<table>", file=filehandle)
                    print(
                        "<thead><tr><th>&nbsp;</th>",
                        "<th>Platz</th>",  # style="text-align: right;"
                        "<th>Paar</th>",  # style="text-align: right;"
                        "<th>Verein</th>",  # style="text-align: right;"
                        "</tr></thead><tbody>",
                        sep="",
                        file=filehandle,
                    )
                    for resline in value[
                        value.Verband == cfg_dict.THEFEDERATION
                    ].iterrows():
                        print(
                            "<tr><td><strong>&nbsp;</strong></td>",
                            "<td>",  # style="text-align: right;"
                            resline[1].Platz,
                            "</td><td>",  # style="text-align: right;"
                            resline[1].Paar,
                            "</td><td>",  # style="text-align: right;"
                            resline[1].Verein,
                            "</td></tr>",
                            sep="",
                            file=filehandle,
                        )
                    print("</tbody></table></figure>", file=filehandle)
                    print("<!-- /wp:table -->", file=filehandle)
                else:
                    print_ul_html(
                        therowiterator=value[
                            value.Verband == cfg_dict.THEFEDERATION
                        ].iterrows(),
                        filehandle=filehandle,
                    )
                print("<!-- wp:spacer -->", file=filehandle)
                print(
                    '<div style="height:100px" aria-hidden="true"'
                    ' class="wp-block-spacer"></div>',
                    file=filehandle,
                )
                print("<!-- /wp:spacer -->", file=filehandle)
                print(
                    '<!-- wp:separator {"className":"is-style-wide"'
                    ',"backgroundColor":"white"} -->',
                    file=filehandle,
                )
                print(
                    '<hr class="wp-block-separator has-text-color has-white-color'
                    " has-alpha-channel-opacity has-white-background-color"
                    ' has-background is-style-wide"/>',
                    file=filehandle,
                )
                print("<!-- /wp:separator -->", file=filehandle)
        print(
            "<!-- wp:paragraph -->",
            '<p>Das Gesamtergebnis ist unter dem <a href="',
            wholereslink,
            '" target="_blank">Link</a> zu finden.</p>',
            "<!-- /wp:paragraph -->",
            sep="",
            file=filehandle,
        )
        print(
            "<!-- wp:paragraph -->",
            "<p>Falls ich ein Paar übersehen habe, ",
            "bitte ich freundlich um eine ",
            "<a href=",
            f'"mailto:{cfg_dict.INFORMEMAIL}',
            '?subject=&Uuml;bersehenes%20Ergebnis"',
            ">Email</a>.</p>",
            "<!-- /wp:paragraph -->",
            sep="",
            file=filehandle,
        )


def presentation_function(
    wholereslink: str,
    allreslinks: list[str],
    tsh_results: list[DataFrame],
    compnames: list[str],
    cfg_dict: AppConfig,
) -> None:
    """Returns result based on config selector."""
    match cfg_dict.RESULTFORMAT:
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
