from argparse import ArgumentParser
from configprocessing import MyConfigT, readconfig

drfparser = ArgumentParser(
    prog="drfp", description="Dance Result Federation Parser", epilog="epi"
)
drfparser.add_argument("URL", type=str)
drfparser.add_argument("-s", "--single", type=bool, default=False)
drfparser.add_argument("-v", "--verbose", type=bool, default=False)
drfparser.add_argument(
    "-f", "--format", type=str, choices=["JOOMLA", "TYPO", "WORDPRESS", "MARKDOWN"]
)
drfparser.add_argument("-o", "--output", type=str)


def main() -> None:
    _ConfigDict: MyConfigT = readconfig()
    args = drfparser.parse_args()
    print(args)
    if args.format:
        _ConfigDict["RESULTFORMAT"] = args.format
    print(_ConfigDict)


if __name__ == "__main__":
    main()
