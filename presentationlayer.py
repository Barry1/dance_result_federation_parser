"""Module for the presentation Layer of the results."""

import logging
from abc import ABC, abstractmethod
from collections.abc import Hashable, Iterator
from contextlib import nullcontext
from io import TextIOWrapper
from typing import TextIO

from pandas import DataFrame, Series

from configprocessing import LOGGERNAME, AppConfig

thelogger: logging.Logger = logging.getLogger(f"{LOGGERNAME}.{__name__}")


class ResultFormatter(ABC):
    """Abstract base for different output formats."""

    def __init__(self, cfg: AppConfig) -> None:
        self.cfg = cfg

    @abstractmethod
    def header(self, federation: str, whole_link: str) -> str: ...

    @abstractmethod
    def competition_header(self, title: str, link: str | None) -> str: ...

    @abstractmethod
    def no_participation(self, federation: str) -> str: ...

    @abstractmethod
    def image_placeholder(self) -> str: ...

    @abstractmethod
    def results_table(self, rows: Iterator[tuple[object, Series]]) -> str: ...

    @abstractmethod
    def results_list(self, rows: Iterator[tuple[object, Series]]) -> str: ...

    @abstractmethod
    def footer(self, whole_link: str, email: str) -> str: ...

    def separator(self) -> str:
        return ""


class JoomlaFormatter(ResultFormatter):
    def header(self, federation: str, whole_link: str) -> str:
        return (
            "<p>Einleitende Worte.</p>\n"
            '<hr id="system-readmore" />\n'
            f"<p>Hier folgend die Ergebnisse "
            f"(nach Verfügbarkeit fortlaufend gepflegt) "
            f"der {federation}-Paare.</p>\n"
            "<!-- =================================================== -->"
        )

    def competition_header(self, title: str, link: str | None) -> str:
        if link and self.cfg.HEADLINELINKS:
            return (
                f'<h2><a href="{link}" target="_blank" '
                f'rel="noopener">{title}</a></h2>'
            )
        return f"<h2>{title}</h2>"

    def no_participation(self, federation: str) -> str:
        return f"<!--\n<p>Leider ohne {federation}-Beteiligung.</p>\n-->"

    def image_placeholder(self) -> str:
        return (
            '<div style="float: right; margin-left: 10px; '
            'text-align: center; font-size: 8pt;">\n'
            '<img src="https://loremflickr.com/150/200/ballroom-dancing" '
            'alt="Beispielfoto" height="200" />\n'
            "<br />Foto: loremflickr.com</div>"
        )

    def results_table(self, rows: Iterator[tuple[object, Series]]) -> str:
        lines = [
            "<table>",
            (
                "<thead><tr><th>&nbsp;</th>"
                '<th style="text-align: right;">Platz</th>'
                '<th style="text-align: right;">Paar</th>'
                '<th style="text-align: right;">Verein</th>'
                "</tr></thead><tbody>"
            ),
        ]
        lines.extend(
            f'<tr><td><strong>&nbsp;</strong></td><td style="text-align: right;">{row.Platz}</td><td style="text-align: right;">{row.Paar}</td><td style="text-align: right;">{row.Verein}</td></tr>'
            for _, row in rows
        )
        lines.append("</tbody></table>")
        return "\n".join(lines)

    def results_list(self, rows: Iterator[tuple[object, Series]]) -> str:
        lines: list[str] = ["<ul>"]
        lines.extend(
            f"<li>{row.Platz} {row.Paar} ({row.Verein})</li>" for _, row in rows
        )
        lines.append("</ul>")
        return "\n".join(lines)

    def footer(self, whole_link: str, email: str) -> str:
        return (
            f"<p>Das Gesamtergebnis ist unter dem "
            f'<a href="{whole_link}" target="_blank">Link</a> zu finden.</p>\n'
            f"<p>Falls ich ein Paar übersehen habe, bitte ich freundlich um eine "
            f'<a href="mailto:{email}?subject=%C3%9Cbersehenes%20Ergebnis">'
            f"Email</a>.</p>"
        )

    def separator(self) -> str:
        return "<!-- =================================================== -->"


class MarkdownFormatter(ResultFormatter):
    def header(self, federation: str, whole_link: str) -> str:
        return (
            f"Die folgenden Inhalte sind die Auswertung der "
            f"[Turnierergebnisse]({whole_link}) für den Verband {federation}.\n\n"
            f"Hier folgend die Ergebnisse "
            f"(nach Verfügbarkeit fortlaufend gepflegt) "
            f"der {federation}-Paare."
        )

    def competition_header(self, title: str, link: str | None) -> str:
        if link and self.cfg.HEADLINELINKS:
            return f"\n## [{title}]({link})\n"
        return f"\n## {title}\n"

    def no_participation(self, federation: str) -> str:
        # Markdown kann Kommentare nicht so elegant → einfach weglassen
        return ""

    def image_placeholder(self) -> str:
        return (
            "![Beispielfoto](https://loremflickr.com/150/200/ballroom-dancing)\n"
            "*Foto: loremflickr.com*"
        )

    def results_table(self, rows: Iterator[tuple[object, Series]]) -> str:
        lines: list[str] = ["|Platz|Paar|Verein|", "|---:|---:|---:|"]
        lines.extend(f"|{row.Platz}|{row.Paar}|{row.Verein}|" for _, row in rows)
        return "\n".join(lines)

    def results_list(self, rows: Iterator[tuple[object, Series]]) -> str:
        return "\n".join(
            f"- {row.Platz} {row.Paar} ({row.Verein})" for _, row in rows
        )

    def footer(self, whole_link: str, email: str) -> str:
        return (
            f"\nDas Gesamtergebnis ist unter dem [Link]({whole_link}) zu finden.\n\n"
            f"Falls ich ein Paar übersehen habe, bitte ich freundlich um eine "
            f"[Email](mailto:{email}?subject=%C3%9Cbersehenes%20Ergebnis)."
        )


class WordPressFormatter(ResultFormatter):
    def header(self, federation: str, whole_link: str) -> str:
        return (
            "<!-- wp:paragraph -->\n"
            "<p>Einleitende Worte.</p>\n"
            "<!-- /wp:paragraph -->\n"
            "<!-- wp:more -->\n"
            "<!--more-->\n"
            "<!-- /wp:more -->\n"
            "<!-- wp:paragraph -->\n"
            f"<p>Hier folgend die Ergebnisse "
            f"(nach Verfügbarkeit fortlaufend gepflegt) "
            f"der {federation}-Paare.</p>\n"
            "<!-- /wp:paragraph -->"
        )

    def competition_header(self, title: str, link: str | None) -> str:
        if link and self.cfg.HEADLINELINKS:
            return (
                "<!-- wp:heading -->\n"
                f'<h2 class="wp-block-heading">'
                f'<a href="{link}" target="_blank" rel="noopener">{title}</a></h2>\n'
                "<!-- /wp:heading -->"
            )
        return (
            "<!-- wp:heading -->\n"
            f'<h2 class="wp-block-heading">{title}</h2>\n'
            "<!-- /wp:heading -->"
        )

    def no_participation(self, federation: str) -> str:
        return ""  # oder auskommentiert wie bei Joomla

    def image_placeholder(self) -> str:
        return (
            '<!-- wp:image {"sizeSlug":"large"} -->\n'
            '<figure class="wp-block-image size-large">\n'
            '<img src="https://loremflickr.com/150/200/ballroom-dancing" '
            'alt="Beispielfoto" />\n'
            '<figcaption class="wp-element-caption">'
            "Foto: loremflickr.com</figcaption>\n"
            "</figure>\n"
            "<!-- /wp:image -->"
        )

    def results_table(self, rows: Iterator[tuple[object, Series]]) -> str:
        # hier kannst du die Joomla-Tabelle wiederverwenden
        # oder eine WordPress-spezifische Variante bauen
        return JoomlaFormatter(self.cfg).results_table(rows)

    def results_list(self, rows: Iterator[tuple[object, Series]]) -> str:
        return JoomlaFormatter(self.cfg).results_list(rows)

    def footer(self, whole_link: str, email: str) -> str:
        return (
            "<!-- wp:paragraph -->\n"
            f"<p>Das Gesamtergebnis ist unter dem "
            f'<a href="{whole_link}" target="_blank">Link</a> zu finden.</p>\n'
            "<!-- /wp:paragraph -->\n"
            "<!-- wp:paragraph -->\n"
            f"<p>Falls ich ein Paar übersehen habe, bitte ich freundlich um eine "
            f'<a href="mailto:{email}?subject=%C3%9Cbersehenes%20Ergebnis">'
            f"Email</a>.</p>\n"
            "<!-- /wp:paragraph -->"
        )


def _get_formatter(cfg: AppConfig) -> ResultFormatter:
    match cfg.RESULTFORMAT:
        case "JOOMLA":
            return JoomlaFormatter(cfg)
        case "WORDPRESS" | "TSH":
            return WordPressFormatter(cfg)
        case "MARKDOWN":
            return MarkdownFormatter(cfg)
        case _:
            thelogger.warning(
                "Unbekanntes RESULTFORMAT %s – verwende Markdown",
                cfg.RESULTFORMAT,
            )
            return MarkdownFormatter(cfg)


def _prepare_df(df: DataFrame, federation: str) -> DataFrame:
    """NAMEDCOUPLE → Federation und filtert."""
    # df = df.copy()
    df.loc[df.Verband == "NAMEDCOUPLE", "Verband"] = federation
    return df[df.Verband == federation]


def render_results(
    formatter: ResultFormatter,
    whole_link: str,
    all_links: list[str],
    results: list[DataFrame],
    comp_names: list[str],
    file: TextIO | None = None,
) -> None:
    """Gemeinsame Logik für alle Formate."""
    cfg: AppConfig = formatter.cfg
    federation = cfg.THEFEDERATION

    print(formatter.header(federation, whole_link), file=file)

    for link, df, title in zip(all_links, results, comp_names):
        filtered: DataFrame = _prepare_df(df, federation)

        if filtered.empty:
            if no_part := formatter.no_participation(federation):
                print(no_part, file=file)
            continue

        print(
            formatter.competition_header(
                title, link if cfg.HEADLINELINKS else None
            ),
            file=file,
        )

        if cfg.IMG_PREP:
            print(formatter.image_placeholder(), file=file)

        rows = filtered.iterrows()
        if cfg.RESULTTABLE:
            print(formatter.results_table(rows), file=file)
        else:
            print(formatter.results_list(rows), file=file)

        if sep := formatter.separator():
            print(sep, file=file)

    print(formatter.footer(whole_link, cfg.INFORMEMAIL), file=file)


def print_results(
    whole_link: str,
    all_links: list[str],
    results: list[DataFrame],
    comp_names: list[str],
    cfg: AppConfig,
) -> None:
    """Einzige öffentliche Funktion."""
    formatter: ResultFormatter = _get_formatter(cfg)

    with (
        open(cfg.OUTPUT, "w", encoding="utf-8")
        if cfg.OUTPUT
        else nullcontext()
    ) as fh:
        render_results(
            formatter, whole_link, all_links, results, comp_names, fh
        )


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
