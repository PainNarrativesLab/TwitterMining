import twitter

from twitter.oauth import read_token_file


def login():
    APP_NAME = ''
    CONSUMER_KEY = ''
    CONSUMER_SECRET = ''
    TOKEN_FILE = ''
    ACCESS_TOKEN = ''
    ACCESS_TOKEN_SECRET = ''
    return twitter.Twitter(domain='api.twitter.com', api_version='1.1',
                           auth=twitter.oauth.OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET))