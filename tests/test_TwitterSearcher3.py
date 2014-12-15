import unittest
import nose
import rednose
from numpy.testing.decorators import setastest
from nose.tools import *
from Loggers import SearchLogger
from TwitterSearcher3 import *
from DaoMocks import *
from TwitterMocks import *

class SearchTest(unittest.TestCase):
    def setUp(self):
        self.object = Search()
        self.redis = RedisDaoMock()
        self.couch = CouchDaoMock()
        self.logger = SearchLogger()

    def tearDown(self):
        self.object = ''
        self.redis = ''
        self.couch = ''
    
    def test_set_twitter_connection(self):
        self.object.set_twitter_connection(login)
        self.assertIsInstance(self.object.twitter_conn, TwitterMock)
    
    def test__get_oldest_tweet(self):
        tweetid = 123456789
        self.redis.set_response(tweetid)
        self.object.set_redis_service(self.redis)
        result = self.object._get_oldest_tweet()
        self.assertEqual(result, tweetid)
        
    def test__get_newest_tweet(self):
        tweetid = 123456789
        self.redis.set_response(tweetid)
        self.object.set_redis_service(self.redis)
        result = self.object._get_newest_tweet()
        self.assertEqual(result, tweetid)

    def test__get_starting_tweet(self):
        tweetid = 123456789
        self.redis.set_response(tweetid)
        self.object.set_redis_service(self.redis)
        result = self.object._get_starting_tweet(True)
        self.assertEqual(result, tweetid)
        #false case
        tweetid2 = 1234566543
        self.redis.set_response(tweetid2)
        self.object.set_redis_service(self.redis)
        result = self.object._get_starting_tweet(False)
        self.assertEqual(result, tweetid2)
        #Null recent case
        tweetid = 123456789
        self.redis.set_response(tweetid)
        self.object.set_redis_service(self.redis)
        result = self.object._get_starting_tweet('')
        self.assertEqual(result, None)
    
    def test__handle_id_field(self):
        bad = 12234
        good = 1234567
        tweet = {'id_str' : good, '_id' : bad}
        result = self.object._handle_id_field(tweet)
        self.assertEqual(result, {'id_str' : good, '_id' : good})

    def test__search_twitter(self):
        tag = 'testtag'
        limittweet = 987665
        self.object.set_twitter_connection(login)
        self.object.limitTweet = limittweet
        result = self.object._search_twitter(tag, True)
        self.assertEqual(result[0], {'query' : tag, 'count' : 100, 'since_id' : limittweet, 'max_id' : None})
        result = self.object._search_twitter(tag, False)
        self.assertEqual(result[0], {'query' : tag, 'count' : 100, 'since_id' : None, 'max_id' : limittweet})
    
    def test__process_search_results(self):
        bad = 12234
        good = 1234567
        tweet1 = {'id_str' : good, '_id' : bad}
        tweet2 = {'id_str' : good, '_id' : bad}
        goodtweet = {'id_str' : good, '_id' : good}
        search_results = {'crap' : ['sltuff'], 'statuses' : [tweet1, tweet2]}
        result = self.object._process_search_results(search_results)
        self.assertEquals(result, [goodtweet, goodtweet])
    
    
        