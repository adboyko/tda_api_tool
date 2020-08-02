import requests
from urllib.parse import unquote
import logging
import json
from datetime import timedelta
import arrow
from time import sleep
from pprint import pprint as pp

"""
    I access a developer.tdameritrade.com API app and query Quotes and Options
"""

TDAM_API_URL = "https://api.tdameritrade.com/"
TDAM_OAUTH = "https://auth.tdameritrade.com/auth"
LOGLEVEL = logging.INFO
ACCESS_TIMEOUT = timedelta(minutes=20)
TOKEN_EXPIRY = timedelta(days=30)


def init_logging():
    log_format = "\033[96m%(asctime)s " \
                 "\033[95m[%(levelname)s] [%(name)s] " \
                 "\033[93m%(message)s\033[0m"
    logging.basicConfig(format=log_format, level=LOGLEVEL)
    logging.info("!!! Logging Setup Complete !!!")
    return logging.getLogger(__name__)


LOG = init_logging()


class DevApp(object):
    def __init__(self):
        try:
            # Load in the existing VARS
            with open("./vars.json", "r") as vars_file:
                app_vars = json.load(vars_file)
        except FileNotFoundError:
            # Trigger first time setup if vars.json is missing
            app_vars = {}
            logging.info("=== First time execution detected ===")
            self._first_time_setup(app_vars)
            logging.info("=== Saving user data to ./vars.json ===")
            with open("./vars.json", "w") as vars_file:
                json.dump(app_vars, vars_file)
            logging.info("=== Saved! ===")

        # Set DevApp object variables
        self._headers = {}
        self.refresh_token = app_vars["REFRESH_TOKEN"]
        self.consume_key = app_vars["CONSUMER_KEY"]
        self.access_token = self._get_access_token()
        self.access_expiry = arrow.now() + ACCESS_TIMEOUT

        # Refresh the refresh_token if needed
        if arrow.get(app_vars["REFRESH_DATE"]) < arrow.now():
            logging.info("Refreshing REFRESH_TOKEN...")
            app_vars["REFRESH_TOKEN"] = self._update_refresh_token()
            app_vars["REFRESH_DATE"] = str(arrow.now() + TOKEN_EXPIRY)
            with open("./vars.json", "w") as vars_file:
                json.dump(app_vars, vars_file)

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
        resp = requests.post(TDAM_API_URL + "v1/oauth2/token", data=payload)
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
        return requests.post(
            TDAM_API_URL + "v1/oauth2/token",
            data=payload
        ).json()["refresh_token"]

    def _get_access_token(self):
        logging.info("Updating access_token...")
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.consume_key
        }
        resp = requests.post(
            TDAM_API_URL + "v1/oauth2/token",
            data=payload
        ).json()["access_token"]
        self._headers.update(
            {"Authorization": "Bearer " + resp}
        )
        return resp

    def renew_access(self):
        self.access_token = self._get_access_token()
        self.access_expiry = arrow.now() + ACCESS_TIMEOUT

    def get_quote(self, ticker):
        logging.info(f"Querying for Quote data of ticker: {ticker}")
        resp = requests.get(
            TDAM_API_URL + f'v1/marketdata/{ticker}/quotes',
            headers=self._headers
        ).json()
        pp(resp)


def main():
    app = DevApp()

    while True:
        if app.access_expiry < arrow.now():
            app.renew_access()
        sleep(1)
        app.get_quote("MCD")
        break


if __name__ == "__main__":
    # noinspection PyBroadException
    try:
        exit(main())
    except Exception:
        LOG.exception("Exception in main()")
        exit(1)
