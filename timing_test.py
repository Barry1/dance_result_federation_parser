#!/bin/env -S poetry run python -OO timing_test.py
import asyncio
import sys

from valuefragments import TimingCM

from dance_result_federation_parser import (
    async_eventurl_to_web,
    eventurl_to_web,
)


class nooutput(object):
    def __init__(self):
        self.stdout = None
        self.stderr = None

    def __enter__(self):
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stderr = self
        sys.stdout = self

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stderr = self.stderr
        sys.stdout = self.stdout

    #        if exc_type is not None:
    #            # Do normal exception handling
    #            raise

    def write(self, x):
        """Write method needed but does nothing."""
        return

    def flush(self):
        """Flush attribute needed but does nothing."""
        return


if __name__ == "__main__":
    print("For best results invoke with")
    print("==> ./timing_test.py & sudo renice -20 $! <==")
    theurl: str = (
        "http://blauesband-berlin.de/Ergebnisse/2019/blauesband2019/index.htm"
    )
    RUN_ASYNC = False
    print("============================================================")
    print("Running Sync")
    with TimingCM():
        with nooutput():
            eventurl_to_web(theurl)
    RUN_ASYNC = True
    print("============================================================")
    print("Running ASync")
    with TimingCM():
        with nooutput():
            asyncio.run(async_eventurl_to_web(theurl))
    print("============================================================")
