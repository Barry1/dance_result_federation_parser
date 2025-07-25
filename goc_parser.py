"""GOC is always a strange thing."""

from joblib import Parallel, delayed
from pandas import DataFrame
from valuefragments import getselectedhreflinks

from configprocessing import MyConfigT, readconfig  # , setuplogger
from presentationlayer import print_wordpress as presentation_function
from stringprocessing import sr_human_comp_info as human_comp_info
from topturnierprocessing import interpret_tt_result as the_interpret_fun

_CFG_DICT: MyConfigT = readconfig()
if __name__ == "__main__":
    import sys

    yearstring = sys.argv[1] if len(sys.argv) > 1 else "2024"
    foundreslinks: list[str] = getselectedhreflinks(thesubstring=yearstring)
    allreslinks: list[str] = [a for a in foundreslinks if a.endswith("index.htm")]
    compnames: list[str] = [
        human_comp_info(turnier_info=thelink) for thelink in allreslinks
    ]
    tsh_results: list[DataFrame] = Parallel(
        n_jobs=1 if __debug__ else -1,
        verbose=10 if __debug__ else 0,
        backend="multiprocessing",  # threading ist nur halb so schnell
    )(delayed(function=the_interpret_fun)(a) for a in allreslinks)
    presentation_function(
        "https://www.goc-stuttgart.de/event-guide/ergebnisarchiv",
        allreslinks,
        tsh_results,
        compnames,
        _CFG_DICT,
    )
