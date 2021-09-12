"""Helpers for String processing."""
from re import sub as re_sub


def cleanevfromentry(singleorg: str) -> str:
    """Remove ev after name of association/club."""
    return re_sub(r"\s+", " ", re_sub(r" e\. ?V\.", "", singleorg)).strip()


def cleanevfrom_dtv_tsh_entry(singleorg: str) -> str:
    """Remove ev from Entry of TSH-association with DTV database."""
    return re_sub(r"– TSH \(\d*\).*", "", cleanevfromentry(singleorg)).strip()


def clean_number_from_couple(couple_str_with_num: str) -> str:
    """Remove starting number from couple string."""
    return (
        couple_str_with_num[0 : couple_str_with_num.rfind("(")].strip()
        if couple_str_with_num.endswith(")")
        else couple_str_with_num
    )
