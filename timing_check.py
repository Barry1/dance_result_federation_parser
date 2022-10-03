#!/bin/env -S poetry run python -OO timing_test.py
import asyncio
import logging
import os
import resource
import sys
from typing import Literal

import psutil
from valuefragments import NoOutput, TimingCM

from dance_result_federation_parser import (
    async_eventurl_to_web,
    eventurl_to_web,
)

if __name__ == "__main__":
    logger: logging.Logger = logging.getLogger("Basti.resultParser")
    logger.disabled = True
    print("For best results invoke with")
    print("==> ./timing_test.py & sudo renice -20 $! ;fg <==")
    theurl: str = (
        "http://blauesband-berlin.de/Ergebnisse/2019/blauesband2019/index.htm"
    )
    print("============================================================")
    RUN_ASYNC: Literal[False, True] = False
    print("Running Sync")
    before = os.times()
    befr = resource.getrusage(resource.RUSAGE_SELF)
    #    print(psutil.Process().cpu_times())
    with TimingCM():
        with NoOutput():
            eventurl_to_web(theurl)
    #    print(psutil.Process().cpu_times())
    after = os.times()
    aftr = resource.getrusage(resource.RUSAGE_SELF)
    print("=========================")
    #    print(before)
    #    print(after)
    print([a - b for (a, b) in zip(after, before)])
    #    print(befr)
    #    print(aftr)
    #    print("============================================================")
    RUN_ASYNC = True
    print("Running ASync")
    #    print(os.times())
    before = os.times()
    with TimingCM():
        with nooutput():
            asyncio.run(async_eventurl_to_web(theurl))
    after = os.times()
    print([a - b for (a, b) in zip(after, before)])
#    print(os.times())
#    print("============================================================")
