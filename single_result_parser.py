"""Module analyzing single competitions not events."""

import logging

from configprocessing import MyConfigT, readconfig, setuplogger
from dance_result_federation_parser import interpret_tt_result
from presentationlayer import presentation_function

thelogger: logging.Logger = setuplogger()
_CFG_DICT: MyConfigT = readconfig()
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        for theurl in sys.argv[1:]:
            thelogger.info("Auswertung von %s", theurl)
            presentation_function(
                theurl,
                [theurl],
                [interpret_tt_result(theurl)],
                ["Turniername"],
                _CFG_DICT,
            )
    else:
        THEURL = (
            "https://www.tbw.de/turnierergebnisse/2021/2021_11_06_Boeblingen/index.htm"
        )
        thelogger.info("Auswertung von %s", THEURL)
        presentation_function(
            THEURL,
            [THEURL],
            [interpret_tt_result(THEURL)],
            ["Turniername"],
            _CFG_DICT,
        )
