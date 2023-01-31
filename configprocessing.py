import logging
from typing import Any, Literal, Optional, TypedDict

import tomllib


def setuplogger(descriptor: str) -> logging.Logger:
    thelogger: logging.Logger = logging.getLogger(f"Basti.{descriptor}")
    # https://docs.python.org/3/library/logging.html#logrecord-attributes
    logformatter: logging.Formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logfilehandler: logging.FileHandler = logging.FileHandler(
        f"{descriptor}.log"
    )
    logfilehandler.setFormatter(logformatter)
    thelogger.addHandler(logfilehandler)
    if __debug__:
        thelogger.setLevel(logging.DEBUG)
    else:
        thelogger.setLevel(logging.INFO)
    return thelogger


class myConfig(TypedDict):
    HEADLINELINKS: Literal[True, False]
    IMG_PREP: Literal[True, False]
    PYANNOTATE: Literal[True, False]
    RUN_ASYNC: Literal[True, False]
    TOTHREAD: Literal[True, False]
    THEFEDERATION: Literal[
        "TSH",
        "HATV",
        "TBW",
        "HTV",
        "Bayern",
        "Berlin",
        "Bremen",
        "NTV",
        "TNW",
        "TRP",
        "SLT",
        "LTV Br",
        "TMV",
        "TVS",
        "TVSA",
        "TTSV",
    ]
    CHECKINGURLS: Optional[list[str]]


def readconfig() -> myConfig:
    """Load config.toml or default configuration."""
    theconfig: myConfig = myConfig()  # type: ignore
    try:
        with open("config.toml", "rb") as f:
            cfg: dict[str, Any] = tomllib.load(f)
    except FileNotFoundError:
        setuplogger("Configuration").info(
            "No file config.toml found, default configuration used."
        )
        cfg: dict[str, Any] = {}
    theconfig["CHECKINGURLS"] = cfg.get("CHECKINGURLS", [])
    theconfig["HEADLINELINKS"] = cfg.get("HEADLINELINKS", False)
    theconfig["IMG_PREP"] = cfg.get("IMG_PREP", False)
    theconfig["PYANNOTATE"] = cfg.get("PYANNOTATE", False)
    theconfig["RUN_ASYNC"] = cfg.get("RUN_ASYNC", True)
    theconfig["TOTHREAD"] = cfg.get("TOTHREAD", False)
    theconfig["THEFEDERATION"] = cfg.get("THEFEDERATION", "TSH")
    return theconfig
