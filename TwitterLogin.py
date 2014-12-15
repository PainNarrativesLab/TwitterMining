import os
import twitter

from twitter.oauth import write_token_file, read_token_file
from twitter.oauth_dance import oauth_dance

def login():
    APP_NAME = 'adaminshanghai_app'
    CONSUMER_KEY = 'W3lp33ZnlUF6gba1y0FLRQ'
    CONSUMER_SECRET = 'vupVVZ81IEnxDpcm7rcJRjRdOIMRqxpQqdhAKvD20'
    TOKEN_FILE = 'out/twitter.oauth'
    ACCESS_TOKEN = '14918616-eq170y0q8pGUbGPevCZTlOiukx4W4xFYejl6yz74'
    ACCESS_TOKEN_SECRET = '9kvz4zul9fNDW831PQawO1NrpcfanDUAqv7Dz2IHw'
    return twitter.Twitter(domain='api.twitter.com', api_version='1.1', auth=twitter.oauth.OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET))