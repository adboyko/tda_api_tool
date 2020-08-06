#!/usr/bin/env python3
"""
   Description
        I access a developer.tdameritrade.com API app and
        query Quotes and Options
"""

import logging
import argparse
import calendar
import sys
from pprint import pprint as pp
from arrow import now as arrownow
from helpers.queries import TDAQueries


def init_logging(loglevel):
    """Set Logging

    Args:
        loglevel (logging.LEVEL): logging.LEVEL where LEVEL is desired LEVEL

    Returns:
        logging object

    """
    log_format = "\033[96m%(asctime)s " \
                 "\033[95m[%(levelname)s] [%(name)s] " \
                 "\033[93m%(message)s\033[0m"
    logging.basicConfig(format=log_format, level=loglevel)
    logging.info("!!! Logging Setup Complete !!!")
    return logging.getLogger(__name__)


def set_arguments():
    """Uses argparse to create a cli-friendly argument acceptor

    Returns:
        argsparse ArgumentParser object

    """
    # Get last day of this month for --optexpiry default
    year_month = arrownow().date().isoformat().split("-")
    year_month[2] = str(
        calendar.monthrange(
            int(year_month[0]), int(year_month[1])
        )[1])
    expiry_default = "-".join(year_month)

    # Add the arguments
    args = argparse.ArgumentParser(description="Interrogate the TDA API!")
    args.add_argument(
        "-s",
        "--symbol",
        type=str,
        help="The ticker sysmble of a stock"
    )
    args.add_argument(
        "-q",
        "--quote",
        action="store_true",
        help="Get the latest quote for symbol(s)"
    )
    args.add_argument(
        "-o",
        "--optchain",
        action="store_true",
        help="Get the latest option chain for symbol. "
             "Use -q for Quote of symbol"
    )
    args.add_argument(
        "-d",
        "--optdepth",
        type=int,
        action="store",
        default=1,
        help="The depth of the option chain above "
             "and below the At-The-Money price"
    )
    args.add_argument(
        "-S",
        "--optstrat",
        type=str,
        action="store",
        nargs='?',
        default="SINGLE",
        choices=["SINGLE", "ANALYTICAL", "COVERED", "VERITCAL", "CALENDAR",
                 "STRANGLE", "STRADDLE", "BUTTERFLY", "CONDOR", "DIAGONAL",
                 "COLLAR", "ROLL"],
        help="The strategy chain to query for. Default is: SINGLE\n"
             "Possible values are: "
             "[ SINGLE | ANALYTICAL | COVERED | VERTICAL | CALENDAR | "
             "STRANGLE | STRADDLE | BUTTERFLY | CONDOR | DIAGONAL | "
             "COLLAR | ROLL ]",
        metavar="OPTSTRAT"
    )
    args.add_argument(
        "-e",
        "--optexpiry",
        type=str,
        action="store",
        nargs='?',
        default=expiry_default,
        metavar="YYYY-MM-DD",
        help="Returns only expirations before this date. "
             f"Default: {expiry_default}"
    )
    args.add_argument(
        "--equities",
        action="store_true",
        help="Print your currently held EQUITY assets"
    )
    args.add_argument(
        "--options",
        action="store_true",
        help="Print your currenetly held OPTION assets"
    )

    return args


def main():
    """The main body for cli.py and currently the entire apitool"""
    args = set_arguments()
    querier = TDAQueries(LOG)

    if len(sys.argv) > 1:
        args = args.parse_args()
        while True:
            if args.quote:
                pp(querier.get_quote(args.symbol))
            if args.optchain:
                pp(querier.get_option_chain(
                    args.symbol,
                    args.optdepth,
                    args.optstrat,
                    args.optexpiry
                ))
            if args.equities:
                querier.display_curr_pos("EQUITY")
            if args.options:
                querier.display_curr_pos("OPTION")
            # sleep(1)
            break
    else:
        if not querier.account.first_time:
            args.print_help()


if __name__ == "__main__":
    # Set logging
    LOG = init_logging(logging.WARNING)

    # Start main()
    # noinspection PyBroadException
    try:
        sys.exit(main())
    except Exception:  # pylint: disable=W0703
        LOG.exception("Exception in main()")
        sys.exit(1)
