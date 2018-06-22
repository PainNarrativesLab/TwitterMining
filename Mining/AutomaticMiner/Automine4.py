"""
Not yet ready
"""

from Mining.Logging.Loggers import SearchLogger

from DatabaseTools.MySQLTools import *
from DatabaseTools.CouchDBTools import *
from DatabaseTools.RedisTools import *
from Mining.DatabaseTools import TwitterSQLService
from Mining.ProcessingTools.TweetDataProcessors import *
from Mining.AutomaticMiner.TwitterSearchTools import *
from Mining.AutomaticMiner.ObserverAndSubscribers import *
from Mining.DatabaseAccessObjects import SqlCredentials
from Mining.AccessManagement.TwitterLogin import *

# Better way to find home
import os
UPATH = os.getenv("HOME")
BASE = '%s/Dropbox/PainNarrativesLab' % UPATH


DB_NAME = 'compiled'
limit = 10000
LOGFILE = '%s/Desktop/twitter_miner_log.txt' % UPATH
# LOGFILE = '/Users/adam/Desktop/twitter_miner_log.txt'
REST = 800  # Interval to rest between runs

SQL_CREDENTIALS = "%s/private_credentials/sql_local_credentials.xml" % BASE
TWITTER_CREDENTIALS = "%s/private_credentials/twittercredentials.xml" % BASE

#search_terms = ['Migraine', 'RSD']

search_terms = ['Spoonie',
                 'CRPS',
                 'Migraine',
                 'RSD',
                 'Fibro',
                 'Fibromyalgia',
                 'Vulvodynia',
                 'ChronicPain',
                 'pain',
                 'endometriosis',
                 'neuropathy',
                 'arthritis',
                 'neuralgia']

# Utility classes
Logger = SearchLogger()
Logger.set_log_file(LOGFILE)
TagHelpers = TagHelpers()

# Initialize couchdb handler classes
couch_dao = CouchDAO()
couch_dao.connect(DB_NAME)
couch_service = CouchService()
couch_service.set_dataservice(couch_dao)
CouchSaver = CouchSaver()
CouchSaver.set_dao(couch_service)

# Initialize redis handler classes
RedisService = RedisService()
RedisSaver = RedisSaver()
RedisSaver.set_dao(RedisService)

# Initialize mysql handler classes
credentials = SqlCredentials.Credentials()
credentials.load_credentials(SQL_CREDENTIALS)
mysql_dao = TwitterSQLService.SQLService( credentials )
# Initialize services for mysql
TweetService = TweetService()
TweetService.set_helper(TagHelpers)
TweetService.set_dao(mysql_dao)

HashtagService = HashtagService()
HashtagService.set_helper(TagHelpers)
HashtagService.set_dao(mysql_dao)

UserService = UserService()
UserService.set_dao(mysql_dao)

MySqlSaver = MySqlSaver()
MySqlSaver.set_services(HashtagService, TweetService, UserService)

# Initialize observer and attach saver objects to it
SaverService = SearchObserver()
SaverService.subscribe_db_saver(RedisSaver)
SaverService.subscribe_db_saver(CouchSaver)
SaverService.subscribe_db_saver(MySqlSaver)

# add some sort of check to make sure everything is ready before starting search

# Initialize classes which perform the searching
Searcher = Search()
Searcher.set_couch_service(CouchService)
Searcher.set_redis_service(RedisService)
Searcher.set_logger(Logger)
Searcher.attach_observer(SaverService)


import twitter


def login(credentials=None):
    APP_NAME = 'adaminshanghai_app'
    CONSUMER_KEY = 'W3lp33ZnlUF6gba1y0FLRQ'
    CONSUMER_SECRET = 'vupVVZ81IEnxDpcm7rcJRjRdOIMRqxpQqdhAKvD20'
    TOKEN_FILE = 'out/twitter.oauth'
    ACCESS_TOKEN = '14918616-eq170y0q8pGUbGPevCZTlOiukx4W4xFYejl6yz74'
    ACCESS_TOKEN_SECRET = '9kvz4zul9fNDW831PQawO1NrpcfanDUAqv7Dz2IHw'
    return twitter.Twitter(domain='api.twitter.com', api_version='1.1',
                           auth=twitter.oauth.OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET))


def getNewerTweets():
    """
    Call this to get the most recent tweets for the search list
    """
    recent = True
    Searcher.set_twitter_connection(login, TWITTER_CREDENTIALS)
    Searcher.run(search_terms, limit, recent, REST)


def getOlderTweets():
    """
    Call this to get tweets older than those already stored
    """
    recent = False
    Searcher.set_twitter_connection(login, TWITTER_CREDENTIALS)
    Searcher.run(search_terms, limit, recent, REST)

getNewerTweets()
