"""Command line interface for Dance Result Federation Parser."""

import sys
from argparse import ArgumentParser, Namespace
from collections.abc import Callable

from dance_result_federation_parser import DanceResultFederationParser


def out_err_stream_changer_factory[**_FunParamP, _FunCallResultT](
    outfilename: str, errfilename: str
) -> Callable[
    [Callable[_FunParamP, _FunCallResultT]],
    Callable[_FunParamP, _FunCallResultT],
]:
    """Decorator Factory changes the output and error streams to filenames."""

    def out_err_stream_changer_decorator(
        function: Callable[_FunParamP, _FunCallResultT],
    ) -> Callable[_FunParamP, _FunCallResultT]:
        """Decorator that changes the output and error streams."""

        def wrapper(
            *args: _FunParamP.args, **kwargs: _FunParamP.kwargs
        ) -> _FunCallResultT:
            """Wrapper function that opens the output and error streams."""
            with (
                open(outfilename, "w") as sys.stdout,
                open(errfilename, "w") as sys.stderr,
            ):
                result: _FunCallResultT = function(*args, **kwargs)
            return result

        return wrapper

    return out_err_stream_changer_decorator


def cli_parser_args() -> Namespace:
    """Return the parsed command line arguments."""
    da_re_fe_parser = ArgumentParser(
        prog="drfp",
        description="Dance Result Federation Parser",
        epilog="Good luck!",
    )
    da_re_fe_parser.add_argument("URL", type=str)
    da_re_fe_parser.add_argument(
        "-s", "--single", default=False, action="store_true"
    )
    da_re_fe_parser.add_argument(
        "-v", "--verbose", default=False, action="store_true"
    )
    da_re_fe_parser.add_argument(
        "-f",
        "--format",
        type=str.lower,
        choices=["joomla", "typo", "wordpress", "markdown"],
    )
    da_re_fe_parser.add_argument(
        "-o", "--output", type=str, help="Output file name"
    )
    return da_re_fe_parser.parse_args()


def main() -> None:
    """Main function for the command line interface."""
    da_re_fe_pa = DanceResultFederationParser()
    args: Namespace = cli_parser_args()
    # print(args)
    # _unneeded = get_dtv_df().sort_index().loc[403:406]
    if args.format:
        da_re_fe_pa.result_format = args.format.upper()
    # print(da_re_fe_pa._ConfigDict)
    if args.single:
        da_re_fe_pa.parsesingle(args.URL)
    else:
        da_re_fe_pa.parse(args.URL)


if __name__ == "__main__":
    main()
