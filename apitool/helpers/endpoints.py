"""
    endpoints management file defining all necessary endpoint URLs
"""
BASE = "https://api.tdameritrade.com/v1/"
OAUTH_TOKEN = BASE + "oauth2/token"
ACCOUNTS_DATA = BASE + "accounts"
GET_SINGLE_QUOTE = BASE + "marketdata/{ticker}/quotes"
GET_OPTION_CHAIN = BASE + "marketdata/chains"
