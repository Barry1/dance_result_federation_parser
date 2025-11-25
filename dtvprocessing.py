"""Module for processing of DTV details."""

import asyncio
import logging
import os
import time
from typing import Literal

import aiofiles
import aiofiles.os
from pandas import DataFrame, read_json, read_parquet

from configprocessing import setuplogger
from stringprocessing import cleanevfromentry

thelogger: logging.Logger = setuplogger()
MAX_CACHE_AGE_IN_SECONDS: int = 7 * 24 * 60 * 60  # eine Woche
PARQUETENGINE: Literal["fastparquet", "pyarrow", "auto"] = "fastparquet"


def create_dtv_df() -> DataFrame:
    """Build dataframe from all organisations taken from DTV.
    New method from 2025-09-07, parser no longer needed."""
    dtv_associations: DataFrame = read_json(
        "https://event.api.tanzsport.de/vereine", orient="records"
    ).set_index("nummer")
    dtv_associations.rename(
        columns={"city": "Ort", "name": "Verein", "federation": "Verband"},
        inplace=True,
    )
    # unter der URL https://event.api.tanzsport.de/events/tags sind
    # die IDs der Verbände mit ihren Namen zu finden.
    # Mit dem zusätzlichen Parametern ?filter=103&filter=1203&filter=1303
    # lässt sich noch mehr finden.
    # 103=Wettbewerbsart
    # 104=Altersgruppe
    # 105=Turnierform
    # 106=Turnierart
    # 107=Klasse
    # 108=Landesverband
    dtv_associations.loc[:, "Verband"] = dtv_associations["Verband"].replace(
        to_replace={
            8: "(TAF)",
            1308: "HTV",
            1408: "HATV",
            1508: "Berlin",
            1608: "Bayern",
            1708: "Brandenburg",
            1808: "LTV Bremen",
            1908: "NTV",
            2008: "Saarland",
            2108: "TBW",
            2208: "TMV",
            2308: "TNW",
            2508: "TRP",
            2608: "TSH",
            2708: "Thüringen",
            2808: "Sachsen",
            2908: "Sachsen-Anhalt",
        }
    )
    dtv_associations.loc[:, "Verein"] = dtv_associations["Verein"].apply(
        func=cleanevfromentry
    )
    dtv_associations.loc[:, "Ort"] = dtv_associations[["Ort"]].apply(
        lambda x: x.str.strip()
    )
    dtv_associations.index = dtv_associations.index.astype(dtype=int)
    thelogger.info("%s", dtv_associations.describe())
    thelogger.debug(
        "%s",
        dtv_associations[["Verband", "Verein"]].groupby(by="Verband").count(),
    )
    thelogger.debug("%s", dtv_associations.loc[404])
    # sqlitedatabase  insertnewclubs(allmatches) - war bei alter API
    return dtv_associations.sort_index()


def get_dtv_df(autoupdate: bool = True) -> DataFrame:
    """Retrieve dataframe of associations from Cache or Web."""
    dtv_associations_cache_file: str = (
        f"{__file__[:__file__.rfind(os.sep)]}/dtv_associations.parquet"
    )
    dtv_associations: DataFrame
    if os.path.exists(dtv_associations_cache_file) and not (
        autoupdate
        and time.time()
        - os.path.getmtime(filename=dtv_associations_cache_file)
        > MAX_CACHE_AGE_IN_SECONDS
    ):  # Cache-Datei vorhanden
        thelogger.info(
            "DTV-Vereinsdaten sind vom %s.",
            time.ctime(os.path.getmtime(filename=dtv_associations_cache_file)),
        )
        dtv_associations = read_parquet(
            path=dtv_associations_cache_file, engine=PARQUETENGINE
        )
    else:  # Keine oder veraltete Cache-Datei vorhanden
        thelogger.info(msg="Aktuelle DTV-Vereinsdaten werden geholt.")
        dtv_associations = create_dtv_df()
        dtv_associations.to_parquet(
            path=dtv_associations_cache_file, engine=PARQUETENGINE
        )
        thelogger.info(msg="DTV-Vereinsdaten aktualisiert.")
    return dtv_associations


async def outputassocfiles() -> None:
    """Write file for each association."""
    dtv_assocs_df: DataFrame = get_dtv_df()
    print(
        dtv_assocs_df.pivot_table(
            index="Verband", values="Verein", aggfunc="count"
        )
    )
    print(dtv_assocs_df[dtv_assocs_df.Verband == "TSH"])
    for verbandsvereine in dtv_assocs_df.groupby(by="Verband"):
        # make folder associations if needed
        verbandsname: str = str(verbandsvereine[0])
        #        verbandsname: str = (
        #            verbandsvereine[0].decode()
        #            if isinstance(verbandsvereine[0], bytes)
        #            else verbandsvereine[0]
        #        )
        if not await aiofiles.os.path.isdir("associations"):
            await aiofiles.os.mkdir(path="associations")
        async with aiofiles.open(
            file=f"associations/{verbandsname}.txt",
            mode="w",
        ) as ausgabedatei:
            await ausgabedatei.write(
                f"{len(verbandsvereine[1])} Vereine im {verbandsname}:\n"
            )
            await ausgabedatei.write(
                verbandsvereine[1][["Verein", "Ort"]].to_string()
            )
            await ausgabedatei.write("\n")


if __name__ == "__main__":
    asyncio.run(main=outputassocfiles())
