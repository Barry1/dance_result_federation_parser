"""Module analyzing single competitions not events."""
import logging

from resultParser import interpret_tt_result, print_tsh_web

thelogger = logging.getLogger("TSH.singleResultParser")
logformatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)  # https://docs.python.org/3/library/logging.html#logrecord-attributes
logfilehandler = logging.FileHandler("singleResultParser.log")
logfilehandler.setFormatter(logformatter)
thelogger.addHandler(logfilehandler)
if __debug__:
    thelogger.setLevel(logging.DEBUG)
else:
    thelogger.setLevel(logging.INFO)
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        for theurl in sys.argv[1:]:
            thelogger.info("Auswertung von %s", theurl)
            print_tsh_web([theurl], [interpret_tt_result(theurl)])
    else:
        THEURL = (
            "https://www.tbw.de/turnierergebnisse/2021"
            + "/2021_11_06_Boeblingen/index.htm"
        )
        thelogger.info("Auswertung von %s", THEURL)
        print_tsh_web([THEURL], [interpret_tt_result(THEURL)])
