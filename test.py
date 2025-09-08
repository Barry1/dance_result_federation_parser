from dance_result_federation_parser import interpret_tt_result
from esvprocessing import get_couples_df

THEURL = (
    "https://ergebnisse.dancecomp.de/2023/4-3006_wdsfopenstdsen2/index.htm"
)
a = interpret_tt_result(THEURL)
b = get_couples_df()
print(a[50:70])
print(b)
c = a.merge(b, on="Paar", how="inner")
print(c)
