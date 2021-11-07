from resultParser import interpret_tt_result, print_tsh_web

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        for theurl in sys.argv[1:]:
            print(f"Auswertung von {theurl}")
            eventurl_to_web(theurl)
    else:
        theurl = "https://www.tbw.de/turnierergebnisse/2021/2021_11_06_Boeblingen_dm_hgrsstd/index.htm"
    print_tsh_web([theurl], [interpret_tt_result(theurl)])
