"""Module for the SQLite-Database handling."""

from __future__ import absolute_import

import logging
import re
import sqlite3
from os import sep
from textwrap import dedent
from typing import Any  # inspect.cleandoc

from pandas import DataFrame, read_sql_query
from valuefragments import portable_timing

from configprocessing import setuplogger

thelogger: logging.Logger = setuplogger()

DATABASE_FILENAME = (
    "DanceCouplesData" + sep + "couples_clubs_federations.sqlite3"
)

CREATE_TABLES_STATEMENT: str = dedent(
    """\
    CREATE TABLE IF NOT EXISTS "Federations" (
        "ID" INTEGER NOT NULL UNIQUE,
        "Abbrev" TEXT NOT NULL UNIQUE,
        "Name" TEXT UNIQUE,
        "URL" TEXT UNIQUE,
        PRIMARY KEY("ID")
    );
    """
    """\
    CREATE TABLE IF NOT EXISTS "Clubs" (
        "ID" INTEGER NOT NULL UNIQUE,
        "Name" TEXT NOT NULL UNIQUE,
        "City" TEXT NOT NULL,
        "FederationID" INTEGER,
        PRIMARY KEY("ID"),
        FOREIGN KEY("FederationID") REFERENCES "Federations"("ID")
    );
    """
    """\
    CREATE TABLE IF NOT EXISTS "Couples" (
        "ID" INTEGER NOT NULL UNIQUE,
        "String" TEXT NOT NULL UNIQUE,
        "ClubID" INTEGER,
        "FromDate" TEXT,
        FOREIGN KEY("ClubID") REFERENCES "Clubs"("ID"),
        PRIMARY KEY("ID" AUTOINCREMENT)
    );
    """
    """\
    CREATE VIEW IF NOT EXISTS "Fed_Club_Count" as
        SELECT Abbrev,count(Clubs.Name)
        FROM Clubs,Federations
        WHERE Federations.ID=Clubs.FederationID
        GROUP BY FederationID
        ORDER BY Abbrev;
    """
    """\
    CREATE VIEW IF NOT EXISTS "CoupleClubFederation" as
        select Couples.String as Paar,Clubs.Name,Federations.Abbrev as Verband
        from Couples
        join Clubs on ClubID=Clubs.ID
        join Federations on Clubs.FederationID=Federations.ID;
    """
    """\
    CREATE VIEW IF NOT EXISTS "activCouplesFederation" as
        select 
            Federations.Abbrev as Verband,
            count(Couples.String) as "aktive Paare"
        from Couples
        join Clubs on ClubID=Clubs.ID
        join Federations on Clubs.FederationID=Federations.ID
        group by Verband
        order by "aktive Paare" desc;
    """
)
INSERT_FEDERATION_STMT = 'INSERT INTO "Federations" ("Abbrev") VALUES(?);'
INSERT_DETAILED_FEDERATION_STMT: str = dedent(
    'INSERT INTO "Federations"'
    ' ("Abbrev","Name","URL")'
    " VALUES(:Abbrev,:Name,:URL);"
)
INSERT_NEW_CLUB_STATEMENT: str = dedent(
    'INSERT INTO "Clubs"'
    ' ("ID", "Name", "City", "FederationID")'
    " SELECT :ID, :Verein, :Ort, ID"
    ' FROM "Federations"'
    ' WHERE "Abbrev"=:Verband'
    ' ON CONFLICT DO UPDATE set "FederationID" = excluded.FederationID;'
)
_INSERT_NEW_CLUB_STATEMENT_REPLACE: str = dedent(
    'REPLACE INTO "Clubs"'
    ' ("ID", "Name", "City", "FederationID")'
    " SELECT :ID, :Verein, :Ort, ID"
    ' FROM "Federations"'
    ' WHERE "Abbrev"=:Verband;'
)
INSERT_COUPLES_STATEMENT: str = dedent(
    'INSERT INTO "Couples"'
    ' ("String", "ClubID", "FromDate")'
    " SELECT :Paar, ID, :Datum"
    ' FROM "Clubs"'
    ' WHERE "Name"=:Verein'
    " ON CONFLICT DO UPDATE"
    ' set "FromDate" = excluded.FromDate where "FromDate"<excluded.FromDate;'
)
_INSERT_COUPLES_STATEMENT_REPLACE: str = dedent(
    'REPLACE INTO "Couples"'
    ' ("String", "ClubID", "FromDate")'
    " SELECT :Paar, ID, :Datum"
    ' FROM "Clubs"'
    ' WHERE "Name"=:Verein'
    #    " ON CONFLICT DO NOTHING;"
    ' ON CONFLICT DO UPDATE set "FromDate" = :Datum where "FromDate"<:Datum;'
)
INSERT_BASECOUPLES_STATEMENT: str = dedent(
    'INSERT INTO "BaseCouples"'
    ' ("HeFirstname", "HeSurname", "SheFirstname",'
    ' "SheSurname","ClubID","FromDate")'
    " Values  (:HeFirstname, :HeSurname, :SheFirstname,"
    " :SheSurname, :ClubID, :FromDate)"
)

# @portable_timing


def insertcouplestodb(sourcedf: DataFrame, tournamentdate: str) -> None:
    """Insert new Couples."""
    # Paar, Verein, Verband
    sourcedf = sourcedf[["Paar", "Verein", "Verband"]].dropna(
        axis=0, subset=["Verband"]
    )
    cpls: list[dict[str, str]] = []
    for _, row in sourcedf.iterrows():
        thelogger.debug(
            "%s | %s | %s", row["Paar"], row["Verein"], row["Verband"]
        )
        cpls.append(
            {
                "Paar": row["Paar"],
                "Verein": row["Verein"],
                "Datum": tournamentdate,
            }
        )
    thelogger.debug("%s", cpls)
    with sqlite3.connect(DATABASE_FILENAME) as con:
        con.set_trace_callback(thelogger.debug)
        con.executemany(INSERT_COUPLES_STATEMENT, cpls)


@portable_timing
def insertnewclubs(tempmatchdict: list[dict[str, str]]) -> None:
    """Insert given clubs and their details into the database."""
    with sqlite3.connect(DATABASE_FILENAME) as con:
        con.set_trace_callback(thelogger.debug)
        con.executemany(INSERT_NEW_CLUB_STATEMENT, tempmatchdict)


def couple_club_federation() -> DataFrame:
    """Get Couples with Clubs and Federations from DB."""
    with sqlite3.connect(
        "file:" + DATABASE_FILENAME + "?mode=ro", uri=True
    ) as con:
        couple_club_federation_df: DataFrame = read_sql_query(
            "SELECT * from CoupleClubFederation", con
        )
    return couple_club_federation_df


@portable_timing
def create_structure() -> None:
    """Setups database and fills the federations abbreviations."""
    # Options for Opening <https://www.sqlite.org/uri.html>
    with sqlite3.connect(
        DATABASE_FILENAME
    ) as con:  # autocommit=False from py3.12
        con.set_trace_callback(thelogger.debug)
        con.executescript(CREATE_TABLES_STATEMENT)
        con.commit()
        # Maybe details from
        # <https://www.tanzsport.de/de/verband/landesverbaende>
        con.execute(INSERT_FEDERATION_STMT, ("Bayern",))
        con.execute(INSERT_FEDERATION_STMT, ("Berlin",))
        con.execute(INSERT_FEDERATION_STMT, ("Bremen",))
        con.execute(INSERT_FEDERATION_STMT, ("HATV",))
        con.execute(INSERT_FEDERATION_STMT, ("HTV",))
        con.execute(INSERT_FEDERATION_STMT, ("LTV Br",))
        con.execute(INSERT_FEDERATION_STMT, ("NTV",))
        con.execute(INSERT_FEDERATION_STMT, ("SLT",))
        con.execute(INSERT_FEDERATION_STMT, ("TBW",))
        con.execute(INSERT_FEDERATION_STMT, ("TMV",))
        con.execute(INSERT_FEDERATION_STMT, ("TNW",))
        con.execute(INSERT_FEDERATION_STMT, ("TRP",))
        con.execute(
            INSERT_DETAILED_FEDERATION_STMT,
            {
                "Abbrev": "TSH",
                "Name": "Tanzsportverband Schleswig-Holstein e. V.",
                "URL": "https://tanzen-in-sh.de/",
            },
        )
        con.execute(INSERT_FEDERATION_STMT, ("TTSV",))
        con.execute(INSERT_FEDERATION_STMT, ("TVS",))
        con.execute(INSERT_FEDERATION_STMT, ("TVSA",))
        con.commit()


def cpltobasecpl() -> None:
    """Searches Couples and derives BaseCouples."""
    theregex = (
        r"(?P<HeSurname>.*), (?P<HeFirstname>.*)"
        + " / "
        + r"(?P<SheSurname>.*), (?P<SheFirstname>.*)"
    )
    with sqlite3.connect(DATABASE_FILENAME) as con:
        couplescursor: sqlite3.Cursor = con.cursor()
        couplescursor.execute(
            "select * from Couples "
            'where String like "%, % / %, %" '
            "and String not in (select String FROM DerivedCouples);"
        )
        allrows: list = couplescursor.fetchall()
        thelogger.info(
            "%i new couples not in base couples found.", len(allrows)
        )
    newbasecouplesdict: list[dict[str, str | Any]] = [
        {
            **re.match(theregex, row[1]).groupdict(),
            "ClubID": row[2],
            "FromDate": row[3],
        }
        for row in allrows
    ]
    with sqlite3.connect(DATABASE_FILENAME) as con:
        con.set_trace_callback(thelogger.debug)
        con.executemany(INSERT_BASECOUPLES_STATEMENT, newbasecouplesdict)


if __name__ == "__main__":
    # create_structure()
    # create_clubs()
    cpltobasecpl()
