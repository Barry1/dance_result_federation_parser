#! /home/ebeling/.local/bin/poetry run python -OO timing_test.py
import asyncio

from valuefragments import TimingCM

from dance_result_federation_parser import (
    async_eventurl_to_web,
    eventurl_to_web,
)

if __name__ == "__main__":
    theurl: str = (
        "http://blauesband-berlin.de/Ergebnisse/2019/blauesband2019/index.htm"
    )
    RUN_ASYNC = False
    print("Running Sync")
    with TimingCM():
        eventurl_to_web(theurl)
    RUN_ASYNC = True
    print("Running ASync")
    with TimingCM():
        asyncio.run(async_eventurl_to_web(theurl))
    print("Hallo")
