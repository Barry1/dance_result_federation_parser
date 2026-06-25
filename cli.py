"""Command line interface for Dance Result Federation Parser."""

from argparse import ArgumentParser, Namespace

from dance_result_federation_parser import DanceResultFederationParser


def cli_parser_args() -> Namespace:
    """Return the parsed command line arguments."""
    da_re_fe_parser = ArgumentParser(
        prog="drfp",
        description="Dance Result Federation Parser",
        epilog="Good luck!",
    )
    da_re_fe_parser.add_argument("URL", type=str)
    da_re_fe_parser.add_argument(
        "-v", "--verbose", default=False, action="store_true"
    )
    da_re_fe_parser.add_argument(
        "-f",
        "--format",
        type=str.lower,
        choices=["joomla", "typo", "wordpress", "markdown"],
        #        default="markdown",
        help="Output format (default: markdown)",
    )
    da_re_fe_parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Output filename (default: stdout)",
    )
    # da_re_fe_parser.set_defaults()
    return da_re_fe_parser.parse_args()


def main() -> None:
    """Main function for the command line interface."""
    da_re_fe_pa = DanceResultFederationParser()
    # temp=cli_parser_args()
    # temp.set_defaults(**dict(da_re_fe_pa._config_dict))
    # temp.set_defaults(**dict(da_re_fe_pa._config_dict))
    args: Namespace = cli_parser_args()
    # print(args)
    # _unneeded = get_dtv_df().sort_index().loc[403:406]
    if args.format:
        da_re_fe_pa.result_format = args.format.upper()
    if args.output:
        da_re_fe_pa.output = args.output
    # print(da_re_fe_pa._config_dict)
    # print("Format okay")
    da_re_fe_pa.parse(args.URL)


if __name__ == "__main__":
    main()
