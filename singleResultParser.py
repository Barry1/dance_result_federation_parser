"""Module analyzing single competitions not events."""
from resultParser import interpret_tt_result, print_tsh_web

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        for theurl in sys.argv[1:]:
            print(f"Auswertung von {theurl}")
            print_tsh_web([theurl], [interpret_tt_result(theurl)])
    else:
        THEURL = "https://www.tbw.de/turnierergebnisse/2021/2021_11_06_Boeblingen_dm_hgrsstd/index.htm"
        print(f"Auswertung von {THEURL}")
        print_tsh_web([THEURL], [interpret_tt_result(THEURL)])
