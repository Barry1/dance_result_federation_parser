#!/bin/env -S poetry run python -OO
"""Try to run methods with and without ASYNC
to find out, what would be the best implementation.
"""

import asyncio
import logging

from valuefragments import NoOutput, TimingCM

from dance_result_federation_parser import (
    async_eventurl_to_web,
    eventurl_to_web,
)

if __name__ == "__main__":
    logger: logging.Logger = logging.getLogger("resultParser")
    logger.disabled = True
    print("For best results invoke with")
    print("==> ./timing_test.py & sudo renice -20 $! ;fg <==")
    theurl: str = (
        "http://blauesband-berlin.de/Ergebnisse/2019/blauesband2019/index.htm"
    )
    print(60 * "=")
    print("Running Sync")
    with TimingCM():
        with NoOutput():
            eventurl_to_web(theurl)
    print(60 * "=")
    print("Running ASync")
    with TimingCM():
        with NoOutput():
            asyncio.run(async_eventurl_to_web(theurl))
    print(60 * "=")
