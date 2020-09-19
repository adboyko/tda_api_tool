"""
    The queries class and methods
"""
from tabulate import tabulate
from helpers.account import TDAAccount
from helpers.endpoints import (GET_SINGLE_QUOTE, GET_OPTION_CHAIN)


class TDAQueries:
    """
        Queries class for substantiating access to API and sending queries
    """
    def __init__(self, logger):
        self.account = TDAAccount()
        self.logger = logger

    @TDAAccount.check_access
    def get_quote(self, symbol):
        """Query for a single Symbol's Quote data

        Args:
            symbol (str): The symbol to get a quote for

        Returns:
            dict: A dictionary rendered from the resulting JSON reply

        """
        self.logger.info(f"Querying for Quote data of ticker: {symbol}")
        resp = self.account.get(
            GET_SINGLE_QUOTE.format(ticker=symbol),
            headers=self.account.headers
        ).json()
        return resp[symbol]

    @TDAAccount.check_access
    def get_option_chain(self, symbol, strike_count, strat, expiry_date):
        """Query for data about a single option chain

        Args:
            symbol (str): The symbol of the underlying stock for the chain
            strike_count (int): Depth above and below the At-The-Money strike
            strat (str): The desired strategy to apply
            expiry_date (str): The furthest out expiry which to query for data

        Returns:
            dict: A dictionary rendered from the resulting JSON reply

        """
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

    @TDAAccount.check_access
    def display_curr_pos(self, pos_type):
        """Display the current EQUITY or OPTION positions of account instance

        Args:
            pos_type (str): Should be one of ['EQUITY', 'OPTION']

        """

        # First, update positions data of pos_type
        self.account.update_positions(pos_type)

        # Now, get the latest price data and display
        table_data = []
        for pos in self.account.positions[pos_type]:
            last_price = self.get_quote(pos["symbol"])["lastPrice"]
            table_data.append([pos["symbol"], pos["quantity"], last_price,
                               int(pos["quantity"]) * last_price])
        print(tabulate(
            table_data,
            headers=["Symbol", "Quantity", "Last Price", "Value"],
            tablefmt="psql",
            numalign="right"
        ))
