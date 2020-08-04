import arrow
from pprint import pprint as pp
from tabulate import tabulate
from tdam.account import TDAAccount
from tdam.endpoints import (GET_SINGLE_QUOTE, GET_OPTION_CHAIN)


class TDAQueries(object):
    """
        Queries class for substantiating access to API and sending queries
    """
    class _Decorators(object):
        """
            Private class to define decorator functions for queries class
        """
        @classmethod
        def check_access(cls, func):
            def query_func(self, *args, **kwargs):
                if self.account.access_expiry < arrow.now():
                    self.account.refresh_token()
                return func(self, *args, **kwargs)
            return query_func

    def __init__(self, logger):
        self.account = TDAAccount()
        self.logger = logger

    @_Decorators.check_access
    def get_quote(self, symbol):
        self.logger.info(f"Querying for Quote data of ticker: {symbol}")
        resp = self.account.get(
            GET_SINGLE_QUOTE.format(ticker=symbol),
            headers=self.account.headers
        ).json()
        return resp[symbol]

    @_Decorators.check_access
    def get_option_chain(self, symbol, strike_count, strat, expiry_date):
        self.logger.info(f"Querying for Option Chain data of ticker: {symbol}")
        parameters = {
            "symbol": symbol,
            "strikeCount": strike_count,
            "strategy": strat,
            "toDate": expiry_date
        }
        resp = self.account.get(
            GET_OPTION_CHAIN,
            params=parameters,
            headers=self.account.headers
        ).json()
        return resp

    @_Decorators.check_access
    def display_curr_pos(self, pos_type):
        acct_pos = f"self.account.{pos_type.lower()}_positions"

        # First, update positions data of pos_type
        self.account.update_positions(pos_type)

        # Now, get the latest price data and display
        table_data = []
        for pos in eval(acct_pos):
            last_price = self.get_quote(pos["symbol"])["lastPrice"]
            table_data.append([pos["symbol"], pos["quantity"], last_price,
                               int(pos["quantity"]) * last_price])
        print(tabulate(
            table_data,
            headers=["Symbol", "Quantity", "Last Price", "Value"],
            tablefmt="psql",
            numalign="right"
        ))
