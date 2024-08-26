"""Module for the SQLite-Database handling."""

import logging
import sqlite3

from pandas import DataFrame
from valuefragments import portable_timing

from configprocessing import setuplogger

thelogger: logging.Logger = setuplogger()

DATABASE_FILENAME = "couples_clubs_federations.db"

CREATE_TABLES_STATEMENT = """
CREATE TABLE IF NOT EXISTS "Federations" (
	"ID"	INTEGER NOT NULL UNIQUE,
	"Abbrev"	TEXT NOT NULL UNIQUE,
	"Name"	TEXT UNIQUE,
	"URL"	TEXT UNIQUE,    
	PRIMARY KEY("ID")
);
CREATE TABLE IF NOT EXISTS "Clubs" (
	"ID"	INTEGER NOT NULL UNIQUE,
	"Name"	TEXT NOT NULL UNIQUE,
	"City"	TEXT NOT NULL,
	"FederationID"	INTEGER,
	PRIMARY KEY("ID"),
	FOREIGN KEY("FederationID") REFERENCES "Federations"("ID")
);
CREATE TABLE IF NOT EXISTS "Couples" (
	"ID"	INTEGER NOT NULL UNIQUE,
	"String"	TEXT NOT NULL UNIQUE,
	"ClubID"	INTEGER,
	"FromDate"	TEXT,
	FOREIGN KEY("ClubID") REFERENCES "Clubs"("ID"),
	PRIMARY KEY("ID" AUTOINCREMENT)
)
CREATE VIEW Fed_Club_Count as
	SELECT Abbrev,count(Clubs.Name)
	FROM Clubs,Federations
	WHERE Federations.ID=Clubs.FederationID
	GROUP BY FederationID
	ORDER BY Abbrev;
"""
INSERT_FEDERATION_STMT = 'INSERT INTO "Federations" ("Abbrev") VALUES(?);'
INSERT_DETAILED_FEDERATION_STMT = """
	INSERT INTO "Federations"
	("Abbrev","Name","URL")
	VALUES(:Abbrev,:Name,:URL);
"""

INSERT_NEW_CLUB_STATEMENT = """INSERT INTO "Clubs"
	("ID", "Name", "City", "FederationID")
	SELECT :ID, :Verein, :Ort, ID
	FROM "Federations"
	WHERE "Abbrev"=:Verband;
"""
INSERT_COUPLES_STATEMENT = """INSERT INTO "Couples"
	("String", "ClubID")
	SELECT :Paar, ID
	FROM "Clubs"
	WHERE "Name"=:Verein
	ON CONFLICT DO NOTHING;
"""


@portable_timing
def insertcouplestodb(sourcedf: DataFrame) -> None:
    """Insert new Couples."""
    # Paar, Verein, Verband
    sourcedf = sourcedf[["Paar", "Verein", "Verband"]].dropna(
        axis=0, subset=["Verband"]
    )
    cpls: list[dict[str, str]] = []
    for _, row in sourcedf.iterrows():
        # thelogger.debug("%s | %s | %s",row["Paar"],row["Verein"],row["Verband"])
        cpls.append({"Paar": row["Paar"], "Verein": row["Verein"]})
    thelogger.debug("%s", cpls)
    with sqlite3.connect(DATABASE_FILENAME) as con:
        con.set_trace_callback(thelogger.debug)
        con.executemany(INSERT_COUPLES_STATEMENT, cpls)
    # select * from couples join clubs on couples.ClubID=Clubs.ID


@portable_timing
def insertnewclubs(tempmatchdict: list[dict[str, str]]) -> None:
    """Insert given clubs and their details into the database."""
    with sqlite3.connect(DATABASE_FILENAME) as con:
        con.set_trace_callback(thelogger.debug)
        con.executemany(INSERT_NEW_CLUB_STATEMENT, tempmatchdict)


@portable_timing
def create_structure() -> None:
    """Setups the expected database and fills the federations with their official abbreviations."""
    # Options for Opening <https://www.sqlite.org/uri.html>
    with sqlite3.connect(
        DATABASE_FILENAME
    ) as con:  # autocommit=False from py3.12
        con.set_trace_callback(thelogger.debug)
        con.executescript(CREATE_TABLES_STATEMENT)
        con.commit()
        # Maybe details from <https://www.tanzsport.de/de/verband/landesverbaende>
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


if __name__ == "__main__":
    create_structure()
    # create_clubs()
