import logging
import argparse
import calendar
from arrow import now as arrownow
from tdam.queries import TDAQueries

"""
    I access a developer.tdameritrade.com API app and query Quotes and Options
"""


def init_logging(loglevel):
    log_format = "\033[96m%(asctime)s " \
                 "\033[95m[%(levelname)s] [%(name)s] " \
                 "\033[93m%(message)s\033[0m"
    logging.basicConfig(format=log_format, level=loglevel)
    logging.info("!!! Logging Setup Complete !!!")
    return logging.getLogger(__name__)


def set_arguments():
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
        help="Get the latest option chain for symbol(s)"
    )
    args.add_argument(
        "-d",
        "--optdepth",
        type=int,
        action="store",
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
        help='''The strategy chain to query for.
                    Default is: SINGLE
                    Possible values are:
                      - SINGLE
                      - ANALYTICAL
                      - COVERED
                      - VERTICAL
                      - CALENDAR
                      - STRANGLE
                      - STRADDLE
                      - BUTTERFLY
                      - CONDOR
                      - DIAGONAL
                      - COLLAR
                      - ROLL 
            '''
    )
    args.add_argument(
        "-e",
        "--optexpiry",
        type=str,
        action="store",
        nargs='?',
        default=expiry_default,
        metavar="YYYY-MM-DD",
        help="Returns only expirations before this date."
             f"Default: {expiry_default}"
    )

    return args


def main():
    args = set_arguments().parse_args()
    querier = TDAQueries(LOG)
    while True:
        if args.quote:
            querier.get_quote(args.symbol)
        if args.optchain:
            querier.get_option_chain(
                args.symbol,
                args.optstrat,
                args.optexpiry,
                args.optstrat
            )
        # sleep(1)
        break


if __name__ == "__main__":
    # Set logging
    LOG = init_logging(logging.WARNING)

    # Start main()
    # noinspection PyBroadException
    try:
        exit(main())
    except Exception:
        LOG.exception("Exception in main()")
        exit(1)
