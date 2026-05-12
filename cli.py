"""Command line interface for Dance Result Federation Parser."""

import asyncio
from argparse import ArgumentParser, Namespace

from configprocessing import MyConfigT, readconfig
from dance_result_federation_parser import (
    DanceResultFederationParser,
    async_eventurl_to_web,
    eventurl_to_web,
    get_dtv_df,
)


def cliParserArgs() -> Namespace:
    """Return the parsed command line arguments."""
    drfparser = ArgumentParser(
        prog="drfp", description="Dance Result Federation Parser", epilog="Good luck!"
    )
    drfparser.add_argument("URL", type=str)
    drfparser.add_argument("-s", "--single", default=False, action="store_true")
    drfparser.add_argument("-v", "--verbose", default=False, action="store_true")
    drfparser.add_argument(
        "-f",
        "--format",
        type=str.lower,
        choices=["joomla", "typo", "wordpress", "markdown"],
    )
    drfparser.add_argument("-o", "--output", type=str)
    return drfparser.parse_args()


def main() -> None:
    """Main function for the command line interface."""
    DRFP = DanceResultFederationParser()
    args: Namespace = cliParserArgs()
    # print(args)
    # _unneeded = get_dtv_df().sort_index().loc[403:406]
    if args.format:
        DRFP.RESULTFORMAT = args.format.upper()
    # print(DRFP._ConfigDict)
    if args.single:
        DRFP.parsesingle(args.URL)
    else:
        DRFP.parse(args.URL)


if __name__ == "__main__":
    main()
