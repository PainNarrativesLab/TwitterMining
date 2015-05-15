import twitter

from twitter.oauth import read_token_file

import xml.etree.ElementTree as ET


class Login(object):

    def __init__(self, credentials_file):
        self.credentials = ET.parse(credentials_file)
        self.APP_NAME = self.credentials.find('app_name').text
        self.CONSUMER_KEY = self.credentials.find('consumer_key').text
        self.CONSUMER_SECRET = self.credentials.find('consumer_secret').text
        self.TOKEN_FILE = 'out/twitter.oauth'
        self.ACCESS_TOKEN = self.credentials.find('access_token').text
        self.ACCESS_TOKEN_SECRET = self.credentials.find('access_token_secret').text


def login(credentials_file):
    """
    Reads the credentials file for the necessary credentials, creates a twitter.Twitter connection and returns it

    Args:
        credentials_file: xml file containing login credentials

    Returns:
        A twitter.Twitter connection object
    """
    credentials = ET.parse(credentials_file)
    APP_NAME = credentials.find('app_name').text
    CONSUMER_KEY = credentials.find('consumer_key').text
    CONSUMER_SECRET = credentials.find('consumer_secret').text
    TOKEN_FILE = 'out/twitter.oauth'
    ACCESS_TOKEN = credentials.find('access_token').text
    ACCESS_TOKEN_SECRET = credentials.find('access_token_secret').text
    return twitter.Twitter(domain='api.twitter.com', api_version='1.1',
                           auth=twitter.oauth.OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET))