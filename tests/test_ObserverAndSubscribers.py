import unittest

from ObserverAndSubscribers import *
from collections import deque

class SearchMock:
    def __init__(self):
        self._observers = []

    def attach_observer(self, observer):
        """
        This attaches an observer object which has an update method to be called when there are new tweets to be stored
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def detach_observer(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify_observers(self, modifier=None):
        for observer in self._observers:
            if modifier != observer:
                observer.update(self)


tweetresults1 = [{'tweet': 'tweet1'}, {'tweet': 'tweet2'}]
tweetresults2 = [{'tweet': 'tweet3'}, {'tweet': 'tweet4'}]
testtweets = [tweetresults1, tweetresults2]


class IDB_Mock(object):
    def __init__(self):
        self.called_list = []

    def save(self, tweet):
        self.called_list.append(tweet)
        return True


class CouchSaverMock(object):
    """
    Mock of the couchSaver in TwitterServiceClasses
    """

    def __init__(self):
        self.tweet = None

    def db(self):
        def save(self, tweet):
            self.tweet = tweet


class CouchServiceMock:
    def make_tweet_views(self):
        pass

    def get_newest_id(self):
        pass

    def get_oldest_id(self):
        pass

    def get_tweetids(self):
        pass

    def get_max_min_ids(self):
        pass

    def get_tweet_texts(self):
        pass

    def make_view(self, name, javascript_function):
        pass


class SearchObserverTest(unittest.TestCase):
    def setUp(self):
        self.target = SearchMock()
        self.object = SearchObserver()
        self.target.attach_observer(self.object)

    def tearDown(self):
        self.object = ''
        self.target = ''

    def test_update(self):
        """
        TODO Rewrite to cover new version
        """
        self.target.tweets = [{'tweet': 'tweet1'}, {'tweet': 'tweet2'}]
        self.target.notify_observers()
        self.assertTrue(len(self.object._tweet_queue) > 0)
        # self.assertEqual(self.object.tweets_to_be_saved.keys()[0], 0)
        # run again to check pool
        self.target.tweets = [{'tweet': 'tweet3'}, {'tweet': 'tweet4'}]
        self.target.notify_observers()
        self.assertTrue(len(self.object._tweet_queue) > 0)
        # self.assertEqual(self.object._tweet_queuetweets_to_be_saved.keys()[0], 0)
        # self.assertEqual(self.object.tweets_to_be_saved.keys()[1], 1)

    def test_add_to_pending_tweets(self):
        self.object._add_to_pending_tweets(testtweets)
        self.assertEqual(len(self.object._tweet_queue), 2)
        self.assertEqual(self.object._tweet_queue.popleft(), tweetresults1)
        self.assertEqual(self.object._tweet_queue.popleft(), tweetresults2)

    def test_get_next_pending_tweet(self):
        # Check returns false if queue empty
        self.assertFalse(self.object._get_next_pending_tweet())
        # Load tweets and check that proper number loaded
        self.object._add_to_pending_tweets(testtweets)
        self.assertEqual(len(self.object._tweet_queue), 2)
        # Check that returns them in proper order
        self.assertEqual(tweetresults1, self.object._get_next_pending_tweet())
        self.assertEqual(tweetresults2, self.object._get_next_pending_tweet())
        self.assertFalse(self.object._get_next_pending_tweet())

    def test_save_pending_tweets(self):
        db1 = IDB_Mock()
        db2 = IDB_Mock()
        self.object._db_objects = [db1, db2]
        self.object._tweet_queue = deque([tweetresults1, tweetresults2])
        self.object.save_pending_tweets()
        self.assertEqual(db1.called_list[0], tweetresults1)
        self.assertEqual(db1.called_list[1], tweetresults2)
        self.assertEqual(db2.called_list[0], tweetresults1)
        self.assertEqual(db2.called_list[1], tweetresults2)
        self.assertEqual(self.object._attempts, self.object._successes)

    def test_subscribe_db_saver(self):
        pass

# class CouchSaverTest(unittest.TestCase):
#     def setUp(self):
#         self.object = CouchSaver()
#         self.couchsaver = CouchSaverMock()
#         self.object.dao = self.couchsaver
#
#     def tearDown(self):
#         self.object = ''
#
#     def test_set_dao(self):
#         pass
#
#     def test_save(self):
#         self.object.save(testtweets[0])
#         # self.assertEqual(self.couchsaver.tweet, testtweets[0])
#         #self.assertTrue(self.object.success)
#
#     def test_success(self):
#         pass


class RedisSaverTest(unittest.TestCase):
    def setUp(self):
        self.object = RedisSaver()
        self.testtweets = [{'id_str': '10001'}, {'id_str': '10002'}, {'id_str': '10003'}]

    def tearDown(self):
        self.object = ''

    def test_set_dao(self):
        pass

    def test_save(self):
        pass

    def test_success(self):
        pass


class MySqlSaverTest(unittest.TestCase):
    def setUp(self):
        self.object = MySqlSaver()
        # self.hashtagservice =

    def tearDown(self):
        self.object = ''

    def test_set_services(self):
        pass

    def test_save(self):
        pass

    def test_success(self):
        pass

if __name__ == '__main__':
    unittest.main()