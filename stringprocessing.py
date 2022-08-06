"""Helpers for String processing."""
import logging
from re import sub as re_sub

thelogger: logging.Logger = logging.getLogger("TSH.resultParser")


def cleanevfromentry(singleorg: str) -> str:
    """Remove ev after name of association/club."""
    return re_sub(r"\s+", " ", re_sub(r" e\. ?V\.", "", singleorg)).strip()


def cleanevfrom_dtv_tsh_entry(singleorg: str) -> str:
    """Remove ev from Entry of TSH-association with DTV database."""
    return re_sub(r"– TSH \(\d*\).*", "", cleanevfromentry(singleorg)).strip()


def clean_number_from_couple(couple_str_with_num: str) -> str:
    """Remove starting number from couple string."""
    return (
        couple_str_with_num[: couple_str_with_num.rfind("(")].strip()
        if couple_str_with_num.endswith(")")
        else couple_str_with_num
    )


def human_comp_info(turnier_info: str) -> str:
    """Convert URL part to human words."""
    [_comp_num, comp_date, comp_desc] = turnier_info.replace("-", "_").split(
        "_", 2
    )
    comp_desc: str = comp_desc.upper()
    comp_desc = comp_desc.replace("HGR", "Hauptgruppe ")
    comp_desc = comp_desc.replace("SEN", "Senioren ")
    comp_desc = comp_desc.replace("LAT", " Latein ")
    comp_desc = comp_desc.replace("STD", " Standard ")
    comp_desc = comp_desc.replace("1", " I ")
    comp_desc = comp_desc.replace("2", " II ")
    comp_desc = comp_desc.replace("3", " III ")
    comp_desc = comp_desc.replace("4", " IV ")
    comp_desc = comp_desc.replace("55", " %% ")  # G55
    comp_desc = comp_desc.replace("5", " V ")
    comp_desc = comp_desc.replace(" %% ", " 55 ")  # G55
    comp_desc = comp_desc.replace("  ", " ")
    comp_desc_human = f"{comp_date[:2]}.{comp_date[2:]}."  # comp_num+':'+
    if comp_desc.startswith("WDSF"):
        comp_desc_human += f" WDSF {comp_desc[4:].strip()}"
    else:
        comp_desc_human += f" DTV {comp_desc[3:].strip()}"
    thelogger.debug("%s ==> %s", turnier_info, comp_desc_human)
    return comp_desc_human
