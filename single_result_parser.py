"""Module analyzing single competitions not events."""

import logging
from typing import Callable

from pandas import DataFrame

from configprocessing import MyConfigT, readconfig, setuplogger
from dance_result_federation_parser import interpret_tt_result
from presentationlayer import print_markdown, print_tsh_web

# from strictly_typed_pandas import DataSet as DataFrame


thelogger: logging.Logger = setuplogger()
_CFG_DICT: MyConfigT = readconfig()
presentationfunction: Callable[
    [str, list[str], list[DataFrame], list[str], MyConfigT], None
]
match _CFG_DICT["RESULTFORMAT"]:
    case "TSH":
        presentationfunction = print_tsh_web
    case "MARKDOWN":
        presentationfunction = print_markdown
#    case _:
#        presentationfunction = None
#        thelogger.debug("Missing or invalid RESULTFORMAT")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        for theurl in sys.argv[1:]:
            thelogger.info("Auswertung von %s", theurl)
            presentationfunction(
                theurl,
                [theurl],
                [interpret_tt_result(theurl)],
                ["Turniername"],
                _CFG_DICT,
            )
    else:
        THEURL = "https://www.tbw.de/turnierergebnisse/2021/2021_11_06_Boeblingen/index.htm"
        thelogger.info("Auswertung von %s", THEURL)
        presentationfunction(
            THEURL,
            [THEURL],
            [interpret_tt_result(THEURL)],
            ["Turniername"],
            _CFG_DICT,
        )
