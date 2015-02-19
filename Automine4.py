"""
Not yet ready
"""

from Loggers import SearchLogger

from SaveToMySQL import *
from TweetDataProcessors import *
from TwitterSearcher3 import *
from ObserverAndSubscribers import *

DB_NAME = 'compiled'
limit = 10000
LOGFILE = '/Users/ars62917/Desktop/twitter_miner_log.txt'
# LOGFILE = '/Users/adam/Desktop/twitter_miner_log.txt'
REST = 800  #Interval to rest between runs

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

#a
#Utility classes
Logger = SearchLogger()
Logger.set_log_file(LOGFILE)
TagHelpers = TagHelpers()

#Initialize couchdb handler classes
CouchService = CouchService(DB_NAME)
CouchSaver = CouchSaver()
CouchSaver.set_dao(CouchService)

#Initialize redis handler classes
RedisService = RedisService()
RedisSaver = RedisSaver()
RedisSaver.set_dao(RedisService)

#Initialize mysql handler classes
mysql_dao = TwitterSQLService.SQLService(test=False, local=True)
#Initialize services for mysql
TweetService = TweetService()
TweetService.set_taghelper(TagHelpers)
TweetService.set_dao(mysql_dao)

HashtagService = HashtagService()
HashtagService.set_taghelper(TagHelpers)
HashtagService.set_dao(mysql_dao)

UserService = UserService()
UserService.set_dao(mysql_dao)

MySqlSaver = MySqlSaver()
MySqlSaver.set_services(HashtagService, TweetService, UserService)

#Intialize observer and attach saver objects to it
SaverService = SearchObserver()
SaverService.subscribe_db_object(RedisSaver)
SaverService.subscribe_db_object(CouchSaver)
SaverService.subscribe_db_object(MySqlSaver)

#add some sort of check to make sure everything is ready before starting search

#Initialize classes which perform the searching
Searcher = Search()
Searcher.set_couch_service(CouchService)
Searcher.set_redis_service(RedisService)
Searcher.set_logger(Logger)
Searcher.attach_observer(SaverService)


def getNewerTweets():
    """
    Call this to get the most recent tweets for the search list
    """
    recent = True
    Searcher.set_twitter_connection(login)
    Searcher.run(search_terms, limit, recent, REST)


def getOlderTweets():
    """
    Call this to get tweets older than those already stored
    """
    recent = False
    Searcher.set_twitter_connection(login)
    Searcher.run(search_terms, limit, recent, REST)

