"""
This contains classes which act as observers of the searcher and then handle saving tweets to the various databases
"""
from collections import deque

class SearchObserver:
    def __init__(self):
        self._db_objects = []
        """ The key to start with in the pool """
        self.basekey = 0
    
        """ The pool of tweets to be saved """
        self._tweet_queue = deque([])
        self.tweets_to_be_saved = dict()
        self.tweets_to_be_saved[0] = None
    
    def update(self, subject):
        """
        When the search is updated it notifies this class by passing itself in here.
        This method controls what is done with it
        """
        tweets = subject.tweets 
        self._new_tweets(tweets)
    
    def _add_to_pending_tweets(self, tweets):
        """
        Adds the incoming tweets to the pool (perhaps should use stack or something like that)
        """
        self._tweet_queue.append(tweets)
        maxkey = max(self.tweets_to_be_saved.keys())    
        #if maxkey is None:
        #    newkey = self.basekey
        #else:
        newkey = maxkey + 1
        self.tweets_to_be_saved[newkey] = tweets
    
    def _get_next_pending_tweet_list(self):
        return self._tweet_queue.popleft()
    
    def _new_tweets(self, tweets):
        if len(tweets) != 0:
            self._add_to_pending_tweets(tweets)
            return tweets
    
    def save_tweets(self, tweets):
        """
        This will call all of the database saver objects (mysql,redis, couch) in turn and hand them a tweet off of
        the queue. Each of those objects has a save method which returns 1 if successfully saved
        """
        numdbs = len(self._db_objects)
        successes = 0
        for db in self._db_objects:
            db.save(tweets)
            db.success()
    
    def subscribe_db_object(self, dbobject):
        """
        Adds DB_Saver implementing object to the list of subscribed object
        """
        self._db_objects.append(dbobject)

class IDB_Saver:
    """
    Interface that the various db saver objects should implement. These objects will be held in
    SearchObserver and then called when the tweets update
    """
    def __init__(self):
        self.success = False
        pass
    
    def save(self, tweets):
        """
        This takes a list of TwitterDataProcessors.Tweet objects
        """
        self.success = False

    def success(self):
        return self.success

class CouchSaver(IDB_Saver):
    
    def __init__(self):
        IDB_Saver.__init__(self)    
    
    def set_dao(self, CouchService):
        """
        This should be a TwitterServiceClasses.CouchService object
        @param CouchService
        @type TwitterServiceClasses.CouchService
        """
        self.dao = CouchService
    
    def save(self, tweets):
        """ save in couchdb
        @param tweets List of TwitterDataProcessors.Tweet objects
        @type tweets list
        """
        try:
            self.success = False
            for tweet in tweets:
                self.dao.db.save(tweet.raw_tweet)
            #Addd checks for success to set flag
            self.success = True
        except Exception as e:
            print "Error in TweetSaverService.CouchSaver %s" % e
    
    #def success(self):
    #    return self.success

class RedisSaver(IDB_Saver):
    def __init__(self):
        IDB_Saver.__init__(self)
        self.success = False
    
    def set_dao(self, RedisService):
        self.dao = RedisService
    
    def _extract_ids(self, tweets):
        """
        Get list of ids from tweets and return list
        """
        ids = []
        [ids.append(x['id_str']) for x in tweets]
        return ids
    
    def save(self, tweets):
        """ save in redis """
        try:
            self.success = False
            for tid in ids:
                self.dao.db.save_tweet_id(tid)
            #Add checks for success to set flag
            self.success = True
        except Exception as e:
            print "Error in TweetSaverService.RedisSaver %s" % e
    

class MySqlSaver(IDB_Saver):
    def __init__(self):
        IDB_Saver.__init__(self)
        self.success = False
    
    def set_services(self, HashtagService, TweetService, UserService):
        self.hashtag_service = HashtagService
        self.tweet_service = TweetService
        self.user_service = UserService
         
    def save(self, tweets):
        """ save in mysql list of Tweet entities """
        try:
            self.success = False
            for tweet in tweets:
                self.hashtag_service.recordHashtags(tweet.tweetID, tweet.hashtags)
                self.user_service.recordUser(tweet.user)
                self.tweet_service.recordTweetData(tweet.tweetID, tweet.tweet_text)
            #Add checks for success to set flag
            self.success = True
        except Exception as e:
            print "Error in TweetSaverService.MySqlSaver %s" % e
    