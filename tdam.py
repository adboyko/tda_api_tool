import logging
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


def main():
    querier = TDAQueries(LOG)
    while True:
        querier.get_quote("MCD")
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
