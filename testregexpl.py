import re

srcstr = "Ebeling, Bastian Dr. / Schmidt, Claudia"
srcstr2 = "Holz, Stefan / Holz, Valentina"
tgtstr = re.sub(r"(.*),(.*)Dr\. ", r"\1, Dr.\2", srcstr)
tgtstr2 = re.sub(r"(.*),(.*)Dr\. ", r"\1, Dr.\2", srcstr2)
print(tgtstr)
print(tgtstr2)
