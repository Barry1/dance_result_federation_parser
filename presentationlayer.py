from pandas import DataFrame
from valuefragments import eprint

from configprocessing import MyConfigT, readconfig

_CFG_DICT: MyConfigT = readconfig()


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
        f"der {_CFG_DICT['THEFEDERATION']}-Paare.",
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
            if _CFG_DICT["HEADLINELINKS"]
            else f"<h2>{turnier_info}</h2>"
        )
        # Falls die gefundenen Ergebnisse aus Paarnamen kommen,
        # wird der Verband künstlich gesetzt:
        # value.Verband[value.Verband == "NAMEDCOUPLE"]
        value.loc[value.Verband == "NAMEDCOUPLE", "Verband"] = _CFG_DICT[
            "THEFEDERATION"
        ]
        if value[value.Verband == _CFG_DICT["THEFEDERATION"]].empty:
            eprint(tournhdr)
            eprint(
                f"<p>Leider ohne {_CFG_DICT['THEFEDERATION']}-Beteiligung.</p>"
            )
            eprint(
                "<!-- =================================================== -->"
            )
        else:
            print(tournhdr)
            if _CFG_DICT["IMG_PREP"]:
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
            if _CFG_DICT["RESULTTABLE"]:
                print("<table>")
                print(
                    "<thead><tr><th>&nbsp;</th>",
                    '<th style="text-align: right;">Platz</th>',
                    '<th style="text-align: right;">Paar</th>',
                    '<th style="text-align: right;">Verein</th></tr></thead><tbody>',
                )
                for resline in value[
                    value.Verband == _CFG_DICT["THEFEDERATION"]
                ].iterrows():
                    print(
                        '<tr><td><strong>&nbsp;</strong></td><td style="text-align: right;">',
                        resline[1].Platz,
                        '</td><td style="text-align: right;">',
                        resline[1].Paar,
                        '</td><td style="text-align: right;">',
                        resline[1].Verein,
                        "</td></tr>",
                    )
                print("</tbody></table>")
            else:
                print("<ul>")
                for resline in value[
                    value.Verband == _CFG_DICT["THEFEDERATION"]
                ].iterrows():
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
        "<p>Falls ich ein Paar übersehen habe, ",
        "bitte ich freundlich um eine ",
        "<a href=",
        '"mailto:ebeling@tanzen-in-sh.de?subject=&Uuml;bersehenes%20Ergebnis"',
        ">Email</a>.</p>",
        sep="",
    )
