"""Command line interface for Dance Result Federation Parser."""

import asyncio
from argparse import ArgumentParser, Namespace

from configprocessing import MyConfigT, readconfig
from dance_result_federation_parser import (
    async_eventurl_to_web,
    eventurl_to_web,
    get_dtv_df,
)

drfparser = ArgumentParser(
    prog="drfp", description="Dance Result Federation Parser", epilog="epi"
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


def main() -> None:
    """Main function for the command line interface."""
    _ConfigDict: MyConfigT = readconfig()
    _unneeded=get_dtv_df().sort_index().loc[403:406]
    args: Namespace = drfparser.parse_args()
    print(args)
    if args.format:
        _ConfigDict["RESULTFORMAT"] = args.format.upper()
    print(_ConfigDict)
    if args.single:
        print("single")
    else:
        print("multi")
        if _ConfigDict["RUN_ASYNC"]:
            asyncio.run(async_eventurl_to_web(args.URL), debug=__debug__)
        else:
            eventurl_to_web(args.URL)


if __name__ == "__main__":
    main()
