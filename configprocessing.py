"""Module for reading configuration from config.toml."""

import logging
import tomllib
from typing import Literal
from pydantic import BaseModel, Field, EmailStr, HttpUrl
LOGGERNAME = "resultParser"

class AppConfig(BaseModel):
    """This class holds the Pydantic-Type-Definition for the configuration."""

    # Hints for Pydantic
    # https://pydantic.dev/docs/validation/latest/get-started/
    # https://medium.com/@marcnealer/a-practical-guide-to-using-pydantic-8aafa7feebf6
    # https://archive.today/Ldxhe
    # https://realpython.com/python-pydantic/
    # https://archive.today/D9q1A

    CHECKINGURLS: list[HttpUrl] = Field(default_factory=list)
    HEADLINELINKS: bool = False
    IMG_PREP: bool = False
    ESVCOUPLES: bool = False
    PYANNOTATE: bool = False
    RUN_ASYNC: bool = True
    TOTHREAD: bool = False
    RESULTTABLE: bool = True
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
    ] = "TSH"
    RESULTFORMAT: Literal["TSH", "JOOMLA", "TYPO", "WORDPRESS", "MARKDOWN"] = (
        "MARKDOWN"
    )
    INFORMEMAIL: EmailStr = "iyslyier@anonaddy.me"


def readconfig() -> AppConfig:
    """Load config.toml or default configuration."""
    thelogger: logging.Logger = logging.getLogger(f"{LOGGERNAME}.{__name__}")
    try:
        with open("config.toml", "rb") as buffered_config_file:
            return AppConfig(**tomllib.load(buffered_config_file))
    except FileNotFoundError:
        thelogger.info("No file config.toml found, using defaults.")
        return AppConfig()
    except Exception as e:
        thelogger.error("Configuration error: %s", e)
        raise
