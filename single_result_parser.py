"""Module analyzing single competitions not events."""

import logging

from configprocessing import setuplogger
from dance_result_federation_parser import interpret_tt_result, print_tsh_web

thelogger: logging.Logger = setuplogger(__name__)  # "singleResultParser"
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        for theurl in sys.argv[1:]:
            thelogger.info("Auswertung von %s", theurl)
            print_tsh_web(
                theurl,
                [theurl],
                [interpret_tt_result(theurl)],
                ["Turniername"],
            )
    else:
        THEURL = (
            "https://www.tbw.de/turnierergebnisse/2021"
            + "/2021_11_06_Boeblingen/index.htm"
        )
        thelogger.info("Auswertung von %s", THEURL)
        print_tsh_web(
            THEURL, [THEURL], [interpret_tt_result(THEURL)], ["Turniername"]
        )
