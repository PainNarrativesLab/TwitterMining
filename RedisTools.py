from DatabaseAccessObjects.RedisDAOs import RedisDAO
from TweetDataProcessors import Extractors
from CouchDBTools import CouchService

__author__ = 'ars62917'


class RedisService(RedisDAO):
    def __init__(self, db=0):
        if db != 0:
            RedisDAO.__init__(self, db)
        else:
            RedisDAO.__init__(self)
        self.loadkeys()

    def loadkeys(self):
        """
        This loads the self.keys property with all the keys in the db
        Mainly used by other methods
        """
        try:
            self.keys = self.db.keys('*')
        except Exception as e:
            print 'failed to load keys %s' % e

    def tag_remove_redis_format(self, redisified_tag):
        junk, sep, tag = redisified_tag.partition(':')
        return tag

    def tweet_id_remove_redis_format(self, redisified_tweetid):
        junk, sep, tweetid = redisified_tweetid.partition('tweet_id:')
        return tweetid

    def get_all_tags(self):
        """
        This pulls all records from the redis database.
        @returns list of dictionaries containing 'tweet_id', and 'tags' where tags is a list of lists
        """
        self.results = []
        keys = self.db.keys('*')
        for k in keys:
            d = {'tweet_id': k, 'tags': list(self.db.smembers(k))}
            self.results.append(d)

    def hashtags_from_search_to_redis(self, search_name):
        """
        This takes tweets recorded in couchdb, pulls out their hashtags and records them in redis.
        Redis is used because the same tweet may have been retrieved by different searches and stored with different documentids in couchdb.
        Redis' set functions condense the duplicates
        """
        self.CS = CouchService(search_name)
        self.CS.get_all_ids()

        for record_id in self.CS.ids:
            if record_id != '_design/index' and record_id != '_design/indexpy':
                print record_id
                tid = 'hashtags:tweet_id:%s' % self.CS.db[record_id]['id_str']
                ht = Extractors.getEntities(self.CS.db[record_id])
                for h in ht['hashtags']:
                    if len(h) >= 1:
                        t = str(h['text']).lower()
                        tag = 'tag:%s' % t
                        print tid, tag
                        self.db.sadd(tid, tag)

    def redis_result_list_fixer(self, redis_result_list):
        tags = []
        for r in redis_result_list:
            t = self.tag_remove_redis_format(r)
            tags.append(t)
        return tags

    def lookup_tweet_id(self, tweetid):
        """
        This looks up whether a tweet id (i.e., id_str) has already been stored in redis
        """
        formatted = RedisFormat.tweet_id_add(tweetid)
        lookup = 'unique_tweets:%s' % formatted
        if lookup in self.keys:
            return True
        else:
            return False

    def remove_redis_format_from_stored_tags(self):
        self.clean_results = []
        for result in self.results:
            rlist = result['tags']
            clist = self.redis_result_list_fixer(rlist)
            self.clean_results.append(clist)

    def save_tweet_id_to_master_list(self, tweetid):
        self.setname = 'tweetIDs'
        try:
            tid = 'unique_tweets:tweet_id:%s' % tweetid
            self.db.sadd(tid, tid)
        except Exception as e:
            print "error %s" % e

    def save_tweet_id(self, tweetid):
        """
        @param tweetid This is the id to be recorded in redis
        @type tweetid Number or string
        """
        # Name of the set that will be storing all the data
        self.setname = 'tweetIDs'
        try:
            #tid = 'unique_tweets:tweet_id:%s' % tweetid
            self.db.sadd(self.setname, tweetid)
        except Exception as e:
            print "error %s" % e

    def get_max_id(self):
        try:
            self.loadkeys()
            mx = max(self.keys)
            self.maxid = RedisFormat.tweet_id_remove(mx)
        except Exception as e:
            print "Error: %s " % e

    def save_graph_storage_error(self, tweetid, errormessage):
        """
        Used to save a record of tweets that weren't recorded in the graph file
        @param tweetid Id of tweet that was not stored in graph file
        @type tweetid int
        @param errormessage Error message thrown by exception
        @type errormessage string

        @todo modify to store error messaage
        """
        self.grapherror_name = 'graphError'
        try:
            self.db.sadd(self.grapherror_name, tweetid)
        except Exception as e:
            print 'Error storing graph error : %s' % e


class RedisFormat:
    """
    Singleton utility to remove and add formatting for storage in redis
    """

    @staticmethod
    def tag_add(tag):
        return 'tag:%s' % tag

    @staticmethod
    def tweet_id_add(tweetid):
        return 'tweet_id:%s' % str(tweetid)

    @staticmethod
    def tag_remove(redisified_tag):
        junk, sep, tag = redisified_tag.partition(':')
        return tag

    @staticmethod
    def tweet_id_remove(redisified_tweetid):
        junk, sep, tweetid = redisified_tweetid.partition('tweet_id:')
        return int(tweetid)


class MaintainMasterTweetList(RedisDAO):
    """
    This goes through all the db's passed in and records the tweet id (i.e., id_str) in a redis set db.
    That creates a master list of tweets.
    Still should keep searches sepatate in couch because not all of them may have been performed at the same intervals
    """

    def __init__(self, list_of_couch_dbs):
        RedisDAO.__init__(self)
        self.ids = []
        for d in list_of_couch_dbs:
            CS = CouchService(d)
            ids = CS.get_tweetids()
            self.ids.extend(ids)
        try:
            for i in self.ids:
                tid = 'unique_tweets:tweet_id:%s' % i
                print tid
                self.db.sadd(tid, tid)
        except Exception as e:
            print "error %s" % e

if __name__ == '__main__':
    pass