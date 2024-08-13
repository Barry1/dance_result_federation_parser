import configparser
from io import StringIO

import requests

# import pandas
from pandas import DataFrame, read_csv

# from strictly_typed_pandas import DataSet as DataFrame
from valuefragments import memoize

from stringprocessing import correcttitleposition


@memoize
def get_esvcredentials() -> dict[str, str]:
    mycredentialsconf: configparser.ConfigParser = configparser.ConfigParser()
    mycredentialsconf.read(".credentials")
    return {
        "action": "login",
        "module": "DefaultMod",
        "user": mycredentialsconf["ESV-LOGIN"]["user"],
        "pass": mycredentialsconf["ESV-LOGIN"]["pass"],
    }


@memoize
def get_couples_df() -> DataFrame:
    """Login to esv and retrieve csv file of couples."""
    readopts = {"encoding": "iso8859_15", "sep": ";", "usecols": ["Paar"]}
    login_url = "https://ev.tanzsport-portal.de"
    couples_url: str = f"{login_url}/Auswertungen/showAuswertung/id/57"
    logout_url: str = f"{login_url}/DefaultMod/logout"
    with requests.Session() as esvsession:
        loginreq: requests.Response = esvsession.post(
            login_url, data=get_esvcredentials()
        )
        assert loginreq.status_code == 200
        whatweneed: requests.Response = esvsession.post(
            couples_url, data={"execute": 1, "export": 1, "print": 0}
        )
        esvsession.get(logout_url)
    couplesdf: DataFrame = read_csv(StringIO(whatweneed.text), **readopts)
    print(couplesdf)
    couplesdf["Paar"] = couplesdf["Paar"].apply(correcttitleposition)
    print(couplesdf)
    return couplesdf


if __name__ == "__main__":
    print(get_couples_df())
