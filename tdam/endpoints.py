"""
    endpoints management file defining all necessary endpoint URLs
"""
BASE = "https://api.tdameritrade.com/v1/"
OAUTH_TOKEN = BASE + "oauth2/token"
GET_SINGLE_QUOTE = BASE + "marketdata/{ticker}/quotes"