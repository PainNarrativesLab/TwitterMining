
import unittest

from TweetSaverService import *
from Loggers import *

class SearchLoggerTest(unittest.TestCase):
    """
    Test for Loggers.SearchLogger
    """
    
    def setUp(self):
        self.object = SearchLogger()
    
    def tearDown(self):
        pass
    
    
    def test_set_log_file(self):
        testpath = '/users/test/test'
        self.object.set_log_file(testpath)
        self.assertEqual(self.object.logfile, testpath)

    def test_run_start(self):
        run_number = 45
        log = ''
        expect_at_front = '---------------------------------'# %s --------------------------- \n' % datetime.now()
        expect_at_end = "Run number: %d \n" % run_number
        
        self.object.run_start(run_number)
        self.assertEqual(self.object.log[:len(expect_at_front)], expect_at_front)
        #self.assertEqual(self.object.log[:len(expect_at_end)], expect_at_end)
    
    def test_limit_tweet_recent_true(self):
        limitTweet = 1234567890
        recent = True
        self.object.limit_tweet(limitTweet, recent)
        expect = "Getting newer tweets \n"
        expect += "starting from tweet %s" % limitTweet
        self.assertEqual(self.object.log, expect)

    def test_limit_tweet_recent_false(self):
        limitTweet = 1234567890
        recent = False
        self.object.limit_tweet(limitTweet, recent)
        expect = "Getting older tweets \n"
        expect += "starting from tweet %s" % limitTweet
        self.assertEqual(self.object.log, expect)
        

    def test_rest_start(self):
        self.object.rest_start()
        expect_at_front= 'start resting: '
        self.assertEqual(self.object.log[:len(expect_at_front)], expect_at_front)
    
    def test_search_term(self):
        testtag = 'catfood'
        self.object.search_term(testtag)
        expect = 'Searching for %s \n' % testtag
        self.assertEqual(self.object.log, expect)
    
    def test_number_of_results(self):
        tag = 'cattoy'
        num_results = 98
        self.object.number_of_results(tag, num_results)
        expect = '    Retrieved %s tweets for search on %s' % (num_results, tag)
        self.object.number_of_results(tag, num_results)

    def test_write_to_file(self):
        pass
        #testpath = '/users/cat/food/nom'
        #self.object.logfile = testpath
        