import arrow
from pprint import pprint as pp
from tdam.account import TDAAccount
from tdam.endpoints import (GET_SINGLE_QUOTE)


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
    def get_quote(self, ticker):
        self.logger.info(f"Querying for Quote data of ticker: {ticker}")
        resp = self.account.get(
            GET_SINGLE_QUOTE.format(ticker=ticker),
            headers=self.account.headers
        ).json()
        pp(resp)
