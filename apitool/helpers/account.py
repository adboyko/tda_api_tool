"""
    The account class and method definitions
"""
import json
from datetime import timedelta
from urllib.parse import unquote
import arrow
import requests
from helpers.endpoints import (OAUTH_TOKEN, ACCOUNTS_DATA)

ACCESS_TIMEOUT = timedelta(minutes=20)
TOKEN_EXPIRY = timedelta(days=30)


class TDAAccount(requests.Session):
    """
        TDA Account class to instantiate the account access session
    """
    def __init__(self):
        super().__init__()
        try:
            self.first_time = False
            # Load in the existing VARS
            with open("./vars.json", "r") as vars_file:
                app_vars = json.load(vars_file)
        except FileNotFoundError:
            self.first_time = True
            # Trigger first time setup if vars.json is missing
            app_vars = {}
            print("=== First time execution detected ===")
            self._first_time_setup(app_vars)
            print("=== Saving user data to ./vars.json ===")
            with open("./vars.json", "w") as vars_file:
                json.dump(app_vars, vars_file)
            print("=== Saved! ===")

        # Refresh the refresh_token if needed
        if arrow.get(app_vars["REFRESH_DATE"]) < arrow.now() \
                or not app_vars["REFRESH_DATE"]:
            print("Refreshing REFRESH_TOKEN...")
            self.refresh_token = app_vars["REFRESH_TOKEN"]
            self.consume_key = app_vars["CONSUMER_KEY"]
            app_vars["REFRESH_TOKEN"] = self._update_refresh_token()
            app_vars["REFRESH_DATE"] = str(arrow.now() + TOKEN_EXPIRY)
            with open("./vars.json", "w") as vars_file:
                json.dump(app_vars, vars_file)

        # Set DevApp object variables
        self.headers = {}
        self.refresh_token = app_vars["REFRESH_TOKEN"]
        self.consume_key = app_vars["CONSUMER_KEY"]
        self.access_token = self._get_access_token()
        self.access_expiry = arrow.now() + ACCESS_TIMEOUT
        self.positions = {
            "EQUITY": self.update_positions("EQUITY"),
            "OPTION": self.update_positions("OPTION")
        }

    @staticmethod
    def _first_time_setup(app_vars):
        print(
            "You will need to generate a consumer_key "
            "and refresh_token before being able to use this tool"
        )
        print(
            "Please visit https://developer.tdameritrade.com/ and"
            " make an account.\nThis is not the same as your "
            "Brokerage account."
        )
        print(
            "Once done, follow this guide to establish "
            "the necessary data for this tool to run:\n"
            "https://developer.tdameritrade.com/content/getting-started"
        )
        print("** Set the callback URL as https://127.0.0.1 **")

        print("-" * 30)
        print("Once done, please provide the consumer_key...\n")
        app_vars["CONSUMER_KEY"] = input("consumer_key?:  ")
        app_vars["CONSUMER_KEY"] += "@AMER.OAUTHAP"
        app_vars["CALLBACK_URI"] = "https://127.0.0.1"

        print(
            "Thank you!\nNow please navigate here and "
            "log in with your Brokerage account:\n"
            "https://auth.tdameritrade.com/auth?"
            f"response_type=code&redirect_uri=https://127.0.0.1"
            f"&client_id={app_vars['CONSUMER_KEY']}"
        )
        print(
            "Once done, please provide the redirected "
            "URL from your browser\n"
        )
        oauth_code = input("Full URL with 'code'?:  ")
        oauth_code = unquote(oauth_code.split("code=")[1])

        print("Now generating your refresh_token and access_token")
        payload = {
            "grant_type": "authorization_code",
            "access_type": "offline",
            "code": oauth_code,
            "client_id": app_vars["CONSUMER_KEY"],
            "redirect_uri": app_vars["CALLBACK_URI"]
        }
        resp = requests.post(OAUTH_TOKEN, data=payload)
        app_vars["REFRESH_TOKEN"] = resp.json()["refresh_token"]
        app_vars["REFRESH_DATE"] = arrow.now() + TOKEN_EXPIRY

        print("Refresh token has been generated. Thank you for setting up")

    def _update_refresh_token(self):
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "access_type": "offline",
            "client_id": self.consume_key
        }
        return self.post(OAUTH_TOKEN, data=payload).json()["refresh_token"]

    def _get_access_token(self):
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.consume_key
        }
        resp = self.post(OAUTH_TOKEN, data=payload).json()["access_token"]
        self.headers.update({"Authorization": "Bearer " + resp})
        return resp

    def renew_access(self):
        """Renew the access token for the account instance"""
        self.access_token = self._get_access_token()
        self.access_expiry = arrow.now() + ACCESS_TIMEOUT

    def update_positions(self, pos_type):
        """Update the equity or option positions of the account instance

        Args:
            pos_type (str): Expecting "EQUITY" or "OPTION"

        Returns:
            list: Returns a list of dicts for each asset and its quantity

        """
        positions = []
        payload = {
            "fields": "positions"
        }
        resp = self.get(
            ACCOUNTS_DATA,
            params=payload,
            headers=self.headers
        ).json()
        if len(resp) != 1:
            return []
        raw_positions = resp[-1]["securitiesAccount"]["positions"]
        for pos in raw_positions:
            if pos["instrument"]["assetType"] == pos_type:
                positions.append(
                    {
                        "symbol": pos["instrument"]["symbol"],
                        "quantity": pos["shortQuantity"] + pos["longQuantity"]
                    }
                )
        return positions

    @classmethod
    def check_access(cls, func):
        """I'm a decorator for checking access token expiry

        Args:
            func: The decorated function

        Returns:
            The function after the decorator actions are taken

        """
        def inner(*args, **kwargs):
            if args[0].account.access_expiry < arrow.now():
                args[0].account.refresh_token()
            return func(*args, **kwargs)
        return inner
