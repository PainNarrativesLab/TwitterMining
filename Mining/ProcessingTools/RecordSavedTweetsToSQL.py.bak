"""
This is a utility for moving saved tweets off of couchdb and onto
the main mysql database
"""
__author__ = 'ars62917'

#from Loggers import SearchLogger
from MySQLTools import *
import CouchDBTools
from CouchDBTools import *
import TwitterSQLService
from TweetDataProcessors import *
from ObserverAndSubscribers import *
from DatabaseAccessObjects import SqlCredentials
import os
import RedisTools



UPATH = os.getenv("HOME")
BASE = UPATH + '/Dropbox/PainNarrativesLab'

DB_NAME = 'compiled'

LOGFILE = '%s/Desktop/twitter_miner_log.txt' % UPATH

SQL_CREDENTIALS = "%s/private_credentials/sql_local_credentials.xml" % BASE
#SQL_CREDENTIALS = "%s/private_credentials/sql_csun_write_credentials.xml" % BASE

# Utility classes
#Logger = SearchLogger()
#Logger.set_log_file(LOGFILE)
tag_helper = TagHelpers()

# Initialize mysql handler classes
credentials = SqlCredentials.Credentials()
credentials.load_credentials(SQL_CREDENTIALS)
mysql_dao = TwitterSQLService.SQLService(credentials)

# Initialize services for mysql
TweetService = TweetService()
TweetService.set_dao(mysql_dao)
TweetService.set_helper(tag_helper)

HashtagService = HashtagService()
HashtagService.set_helper(tag_helper)
HashtagService.set_dao(mysql_dao)

UserService = UserService()
UserService.set_dao(mysql_dao)


def checker(tweetid):
    if tweetid is None:
        return False
    else:
        return True

errors = 0
tweets = 0
attempts = 0
error_ids = []
#minerip = 169.254.203.246

tig = RedisTools.TweetIdGetter(storage_set='novelids')
tweet_retriever = CouchDBTools.TweetRetriever()
#numtweets = tig.make_queue()
#print "%s tweetids to process" % numtweets
go = True
while True:
    try:
        tweetid = tig.get_tweetid()
        go = checker(tweetid)
        attempts += 1
        tweet = tweet_retriever.get_tweet(tweetid)
        UserService.recordUser(tweet.user)
        TweetService.recordTweetData(tweet.tweetID, tweet)
        for tag in tweet.hashtags:
            HashtagService.recordHashtags(tweet.tweetID, tag)
        tweets += 1
    except Exception as e:
        error_ids.append(tweetid)
        print "Error %s" % e

# # Initialize couchdb handler and connect to server
# couch_dao = CouchDAO(server='http://169.254.113.17:5984')
# couch_dao.connect(DB_NAME)
# # Get result set
# result = couch_dao.query("""function(doc){emit (doc.id, doc);}""")

##errors = 0
##tweets = 0
##attempts = 0
##
##try:
##    for r in result:
##        attempts += 1
##        UserService.recordUser(r['value']['user'])
##        TweetService.recordTweetData(r['id'], r['value'])
##        tags = tag_helper.getHashtags(r['value'])
##        if len(tags) > 0:
##            HashtagService.recordHashtags(r['id'], tags)
##        tweets += 1
##except Exception as e:
##    errors += 1
##    print e

##finally:
print '%i tweets processed' % attempts
print '%i errors in processing tweets' % errors
print '%i tweets successfully processed' % tweets
