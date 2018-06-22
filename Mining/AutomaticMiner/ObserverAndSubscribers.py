"""
This contains an observer class and the subscribers it notifies.

The various subscribers will be held inside SearchObserver.
The process which handles the actual searching of twitter will hold SearchObserver in it.
Once a search completes, SearchObserver will notify the subscribers in turn so that they can save
the new tweets to their respective databases.

"""
from collections import deque

from Mining.Errors.ErrorClasses import *


class ISearchObserver(object):
    """
    Interface for Observer for twitter searches with objects that handles database saving subscribed. When a search retreives
    new tweets, it calls update(). The observer then calls each subscribed database service object in turn to save
    """

    def update(self, subject):
        raise NotImplementedError

    def subscribe_db_saver(self, dbobject):
        raise NotImplementedError

    def save_pending_tweets(self):
        raise NotImplementedError

    def _add_to_pending_tweets(self, tweets):
        raise NotImplementedError

    def _get_next_pending_tweet(self):
        raise NotImplementedError

    def _save_tweet(self, tweet):
        raise NotImplementedError


class SearchObserver(ISearchObserver):
    """
    Observer for twitter searches with objects that handles database saving subscribed. When a search retreives
    new tweets, it calls update(). The observer then calls each subscribed database service object in turn to save
    
    Attributes:
        _attempts: Integer of the number of distinct save attempts (should = number_tweets_retrieved * number_db_savers)
        _db_objects: List of db connection objects (should implement IDB_Saver)
        _successes: Integer of the number of save attempts that were successful
        _tweet_queue: Deque holding the tweets to be processed. Append new tweets to the right; pop from left
    """

    def __init__(self):
        ISearchObserver.__init__(self)
        self._db_objects = []
        self._attempts = 0
        self._successes = 0
        self._tweet_queue = deque([])

    def update(self, subject):
        """
        When the search is updated it notifies this class by passing itself in here.
        This method controls what is done with it
        
        Args:
            subject: Object with a tweets property 
        """
        tweets = subject.tweets
        if len(tweets) > 0:
            self._add_to_pending_tweets(tweets)
        self.save_pending_tweets()

    def subscribe_db_saver(self, dbobject):
        """
        Adds IDB_Saver implementing object to the list of subscribed objects

        Args:
            dbobject: Object implementing the IDB_Saver interface
        """
        self._db_objects.append(dbobject)

    def save_pending_tweets(self):
        """
        Attempts to save all pending tweets
        """
        while True:
            tweet = self._get_next_pending_tweet()
            if tweet is False:
                return False
            else:
                self._save_tweet(tweet)

    def _add_to_pending_tweets(self, tweets):
        """
        Adds the incoming tweets to the pool to be recorded

        Args:
            List of dictionary objects returned by the searcher containing tweets
        """
        [self._tweet_queue.append(tweet) for tweet in tweets]

    def _get_next_pending_tweet(self):
        """
        Gets the next tweet from the list of pending tweets by popping it from the left side of the deque

        Returns:
            A tweet dictionary ready to be recorded or False if the queue is empty
        """
        try:
            return self._tweet_queue.popleft()
        except:
            return False

    # def _new_tweets(self, tweets):
    #     """
    #     Adds new tweets to the pool to be recorded
    #     Args:
    #         tweets: List of dictionary objects returned by the searcher containing tweets
    #
    #     Returns:
    #         The incoming tweets
    #     """
    #     if len(tweets) != 0:
    #         self._add_to_pending_tweets(tweets)
    #         return tweets

    def _save_tweet(self, tweet):
        """
        This will call each of the database saver objects (mysql,redis, couch) in turn and hand them a tweet off of
        the queue. Each of those objects has a save method which returns 1 if there were no errors in saving.
        The subscriber should handle and log any errors internally.

        Args:
            tweet: Tweet dictionary object for saving

        TODO: Perhaps have this running on a separate thread so that the calls to update won't be held up by save tasks?
        """
        for db in self._db_objects:
            # print "called %s /n" % db.name
            self._attempts += 1
            result = db.save(tweet)
            if result is True:
                self._successes += 1


class IDB_Saver(object):
    """
    Interface that objects which handle saving tweets to various databases should implement.
    These objects will be held in SearchObserver and then called when the tweets update
    
    Attributes:
        success: Boolean of whether the tweet has been saved. Default false
    """

    def __init__(self):
        self.success = False
        pass

    def save(self, tweets):
        """
        This saves the tweets. Should also handle any errors by logging them without disrupting other proecesses

        TODO Perhaps make the input a list of TwitterDataProcessors.Tweet objects
        Args:
            tweets: List of tweets to record

        Returns:
            False if at least one recording attempt fails. True otherwise
        """
        raise NotImplementedError()


class CouchSaver(IDB_Saver):
    """
    Subscriber to observer. Saves the new tweets to couchdb
    """

    def __init__(self):
        IDB_Saver.__init__(self)
        self.name = 'couchsaver'

    def set_dao(self, CouchService):
        """
        Sets the couch db access handler
        
        Args:
            CouchService: This is a TwitterServiceClasses.CouchService object which handles the db access
        """
        self.dao = CouchService

    def save(self, tweet):
        """
        Saves a tweet into couchdb

        Args:
            tweet: A TwitterDataProcessors.Tweet object

        Returns:
            Boolean of whether succeeded or failed
        """
        self.success = True
        try:
            self.dao.dao.save(tweet.raw_tweet)
        except SaverError("TweetSaverService.CouchSaver", tweet):
            self.success = False
        return self.success

    def save_list(self, tweets):
        """
        Saves a list of tweets into couchdb
        Not currently used

        Args:
            tweets: List of TwitterDataProcessors.Tweet objects

        Returns:
            Boolean of whether succeeded or failed
        """
        self.success = True
        for tweet in tweets:
            try:
                self.dao.dao.save(tweet.raw_tweet)
            except SaverError("TweetSaverService.CouchSaver", tweet):
                self.success = False
        return self.success


class RedisSaver(IDB_Saver):
    """
    Subscriber to SearchObserver. Saves new tweet ids to redis

    Attributes:
        success: Boolean of whether the save attempt was successful. Default False
        dao: RedisService: RedisTools.RedisService object which will handle saving the tweets
    """

    def __init__(self):
        IDB_Saver.__init__(self)
        self.success = False
        self.name = 'redissaver'

    def set_dao(self, redis_service):
        """
        Load redis server connection handler

        Args:
            redis_service: RedisTools.RedisService object which will handle saving the tweets
        """
        self.dao = redis_service

    def save(self, tweet):
        """
        Saves a tweet to redis
        Args:
            tweet: tweet: A TwitterDataProcessors.Tweet object
        """
        self.success = True
        tid = tweet.tweetID
        if tid:
            try:
                self.dao.save_tweet_id(tid)
            except SaverError("TweetSaverService.RedisSaver", tid):
                self.success = False
        return self.success

    @staticmethod
    def _extract_ids(tweets):
        """
        Get list of ids from tweets and return list
        Args:
            tweets: List of dictionary like objects with a key 'id_str'
        """
        ids = []
        [ids.append(x['id_str']) for x in tweets]
        return ids

    def save_list(self, tweets):
        """
        Saves tweets to redis.
        Not actually used now
        Args:
            tweets: List of tweet dicts
        """
        self.success = True
        ids = self._extract_ids(tweets)
        for tid in ids:
            try:
                self.dao.save_tweet_id(tid)
            except SaverError("TweetSaverService.RedisSaver", tid):
                self.success = False
        return self.success


class MySqlSaver(IDB_Saver):
    """
    Subscriber to SearchObserver. Handles saving to mysql database

    Attributes:
        hashtag_service: SaveToMySQL.HashtagService
        tweet_service: SaveToMySQL.TweetService
        user_service: SaveToMySQL.UserService
        success: Boolean of whether attempted save was successful
    """

    def __init__(self):
        IDB_Saver.__init__(self)
        self.success = False
        self.name = 'mysqlsaver'

    def set_services(self, HashtagService, TweetService, UserService):
        """
        Loads in the service classes used via the observer. Each should already be
        initialized with its database connection set.

        Args:
            HashtagService: SaveToMySQL.HashtagService This will save the hashtags to the db
            TweetService: SaveToMySQL.TweetService This will save the tweet to the db
            UserService: SaveToMySQL.UserService This will save information about the user to the db
        """
        self.hashtag_service = HashtagService
        self.tweet_service = TweetService
        self.user_service = UserService

    def save(self, tweet):
        """
        Saves a tweet to mysql
        Args:
            tweet: TweetDataProcessor.Tweet object

        Returns:
            False if at least one recording attempt fails. True otherwise
        """
        self.success = True
        try:
            self.user_service.recordUser(tweet.user)
            self.tweet_service.recordTweetData(tweet.tweetID, tweet)
            self.hashtag_service.recordHashtags(tweet.tweetID, tweet.hashtags)
        except SaverError("TweetSaverService.MySQLSaver", tweet):
            self.success = False
            # print "Error in TweetSaverService.MySqlSaver %s" % e
        return self.success

    def save_list(self, tweets):
        """
        save in mysql list of Tweet entities.
        Not currently used
        Args:
            tweets: List of tweets to record

        Returns:
            False if at least one recording attempt fails. True otherwise
        """
        self.success = True
        for tweet in tweets:
            try:
                self.hashtag_service.recordHashtags(tweet.tweetID, tweet.hashtags)
                self.user_service.recordUser(tweet.user)
                self.tweet_service.recordTweetData(tweet.tweetID, tweet.tweet_text)
            except SaverError("TweetSaverService.RedisSaver", tweet):
                self.success = False
                # print "Error in TweetSaverService.MySqlSaver %s" % e
        return self.success


if __name__ == '__main__':
    pass