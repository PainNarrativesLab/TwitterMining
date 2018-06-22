"""
@todo figure out how to do emoticons as inputs to formatter and HTML entities tests
@todo figure out how to keep formatter from failing on integer inputs (problem probably with the str.lower() call)
"""
import unittest

from numpy.testing.decorators import setastest

from tests.DaoMocks import *
from tests.TwitterProjectTestEntities import *
from Mining.DatabaseTools.MySQLTools import *
from Mining.DatabaseAccessObjects.SqlCredentials import TestingCredentials
from Mining.ProcessingTools.TweetDataProcessors import *


class TweetServiceTest(unittest.TestCase):
    def setUp(self):
        self.object = TweetService()
        self.dao = DaoMock()
        self.helper = TagHelpers()

    def tearDown(self):
        self.object = ''
        self.dao = ''

    def test_recordTweetData(self):
        tweet = test_tweet
        expectedval = [tweet['id'], tweet['text'],
                       tweet['favorite_count'], tweet['source'],
                       tweet['retweeted'], tweet['in_reply_to_screen_name'],
                       tweet['retweet_count'], tweet['favorited'],
                       tweet['user']['id'], tweet['lang'], tweet['created_at']]
        self.object.set_dao(self.dao)
        self.object.set_helper(self.helper)
        # Tested method
        self.object.recordTweetData(tweet['id'], tweet)
        # Assertions
        self.assertTrue(len(self.dao.log) is 1)
        self.assertEqual(self.dao.log[0]['val'], expectedval)
        self.assertEqual(self.dao.log[0]['command'], 'executeQuery')


class HashtagServiceTest(unittest.TestCase):
    def setUp(self):
        self.credentials = TestingCredentials()
        self.object = HashtagService()
        self.dao = DaoMock()
        self.object.set_dao(self.dao)
        self.object.set_helper(TagHelpers())
        self.tweetid = 1245678964
        self.tagid = 1235665433
        self.tagtext = 'fakeTag'
        self.formatted_tagtext = 'faketag'

    def tearDown(self):
        self.object.dao = ''
        self.dao = ''

    def test_getTagID(self):
        self.object.taghelper = TagHelpers()
        result = self.object.getTagID(self.tagtext)
        self.assertEqual(self.dao.log[0]['query'], "SELECT tagID FROM hashtags WHERE hashtag = %s")
        self.assertEqual(self.dao.log[0]['val'], [self.formatted_tagtext])
        self.assertEqual(self.dao.log[0]['command'], 'returnOne')

    def test__recordTagText(self):
        self.object.taghelper = TagHelpers()
        self.object._recordTagText(self.tagtext)
        self.assertEqual(self.dao.log[0]['query'], "INSERT INTO hashtags (hashtag) VALUES (%s)")
        self.assertEqual(self.dao.log[0]['val'], [self.tagtext.lower()])
        self.assertEqual(self.dao.log[0]['command'], 'executeQuery')

    def test__recordTagAssoc(self):
        self.object._recordTagAssoc(self.tweetid, self.tagid)
        self.assertEqual(self.dao.log[0]['query'], "INSERT IGNORE INTO tweetsXtags (tweetID, tagID) VALUES (%s, %s)")
        self.assertEqual(self.dao.log[0]['val'], [self.tweetid, self.tagid])
        self.assertEqual(self.dao.log[0]['command'], 'executeQuery')

    def test_recordHashtags_new_tags(self):
        tags = ['test0tag']
        dao = DaoMock()
        dao.set_response(None)
        self.object.set_dao(dao)
        self.object.recordHashtags(self.tweetid, tags)
        self.assertEqual(len(dao.log), 4)
        self.assertEqual(dao.log[0]['query'], """SELECT tagID FROM hashtags WHERE hashtag = %s""")
        self.assertEqual(dao.log[1]['query'], """INSERT INTO hashtags (hashtag) VALUES (%s)""")
        self.assertEqual(dao.log[2]['query'], """SELECT tagID FROM hashtags WHERE hashtag = %s""")
        self.assertEqual(dao.log[3]['query'], """INSERT IGNORE INTO tweetsXtags (tweetID, tagID) VALUES (%s, %s)""")
        print(dao.log)

    def test_recordHashtags(self):
        tags = ['test0tag']
        dao = DaoMock()
        dao.set_response({'tagID': 123})
        self.object.set_dao(dao)
        self.object.recordHashtags(self.tweetid, tags)
        self.assertEqual(dao.log[0]['query'], """SELECT tagID FROM hashtags WHERE hashtag = %s""")
        self.assertEqual(self.dao.log[0]['val'], [tags[0]])
        self.assertEqual(dao.log[3]['query'], """INSERT IGNORE INTO tweetsXtags (tweetID, tagID) VALUES (%s, %s)""")
        self.assertEqual(self.dao.log[3]['val'], [self.tweetid, 123])
        self.assertEqual(len(dao.log), 2)
        print(dao.log)


class UserServiceTest(unittest.TestCase):
    def setUp(self):
        self.object = UserService()

    def tearDown(self):
        pass

    @setastest(True)
    def test_check_user(self):
        dao = DaoMock()
        dao.results = [0, 1, 2]
        self.object.set_dao(dao)
        userid = "4567890"
        self.assertTrue(self.object.check_user(userid))
        self.assertEqual(dao.val, [userid])
        self.assertEqual(dao.query, """SELECT userID FROM users WHERE userID = %s""")
        dao1 = DaoMock()
        dao1.results = []
        dao1.set_response([])
        self.object.set_dao(dao1)
        self.assertFalse(self.object.check_user(userid))

    def test__filter_userDict(self):
        test_dict = {"id_str": "319297935",
                     "utc_offset": 7200,
                     "statuses_count": 137,
                     "description": "Student seksuologie @KU_Leuven | KSA",
                     "friends_count": 81,
                     "location": "Leuven",
                     "profile_sidebar_fill_color": 'badvalue',
                     'is_translator': 'badvalue',
                     'geo_enabled': 'badvalue',
                     'protected': 'badvalue'}
        expected_keys = ["id_str",
                         "utc_offset",
                         "statuses_count",
                         "description",
                         "friends_count",
                         "location"]
        removed_keys = ["profile_sidebar_fill_color",
                        'is_translator',
                        'geo_enabled',
                        'protected']
        result = self.object._filter_userDict(test_dict)
        [self.assertTrue(x in result) for x in expected_keys]
        [self.assertTrue(x not in result) for x in removed_keys]

    def test__add_user_to_user_table(self):
        expectedQuery = """INSERT INTO users (userID) VALUES (%s)"""
        userid = "4567890"
        dao = DaoMock()
        self.object.set_dao(dao)
        self.object._add_user_to_user_table(userid)
        self.assertEqual('executeQuery', dao.result)
        self.assertEqual(dao.query, expectedQuery)
        self.assertEqual(dao.val, [userid])

    def test__update_user_table_fields(self):
        userid = "4567890"
        dao = DaoMock()
        testfields = ['test0', 'test1']
        testdict = {'id': userid, 'test0': 'test0val', 'test1': 'test1val'}
        self.object.set_dao(dao)
        self.object._update_user_table_fields(userid, testfields, testdict)
        self.assertEqual(len(dao.log), 2)
        for x in dao.log:
            self.assertEqual(x['command'], 'executeQuery')
            self.assertEqual(x['query'], "UPDATE users SET test%s = %%s WHERE userID = %%s" % x['run_num'])
            self.assertEqual(x['val'], ["test%sval" % x['run_num'], userid])

    def test_createUser(self):
        dao = DaoMock()
        dao.results = [0, 1]  # So that will think user is inserted on checkuser step
        userid = "4567890"
        testfields = ['test0', 'test1']
        testdict = {'id': userid, 'test0': 'test0val', 'test1': 'test1val'}
        goodqueries = ["UPDATE users SET test0 = %s WHERE userID = %s", "UPDATE users SET test1 = %s WHERE userID = %s"]
        goodtestvals = ['test0val', 'test1val']
        self.object.set_dao(dao)
        # Target method
        self.object.createUser(testdict)
        # Assertions
        self.assertEqual(len(dao.log), 4)
        # add user
        self.assertEqual(dao.log[0]['command'], 'executeQuery')
        self.assertEqual(dao.log[0]['query'], "INSERT INTO users (userID) VALUES (%s)")
        self.assertEqual(dao.log[0]['val'], [userid])
        # check user
        self.assertEqual(dao.log[1]['command'], 'returnAll')
        self.assertEqual(dao.log[1]['query'], "SELECT userID FROM users WHERE userID = %s")
        self.assertEqual(dao.log[1]['val'], [userid])
        # update fields
        cnt = 0
        for x in dao.log[2:]:
            self.assertEqual(x['run_num'], cnt + 2)
            self.assertEqual(x['command'], 'executeQuery')
            self.assertTrue(x['query'] in goodqueries)  #field updates might not be in same order
            self.assertEqual(x['val'][1], userid)
            self.assertTrue(x['val'][0] in goodtestvals)
            cnt += 1

    def test_createUser_errors(self):
        """
        Makes sure that throws errors as appropriate
        @todo createUser error handling
        """
        pass

    def test_recordUser_userPreExists(self):
        """
        Three main cases: user preexists, user needs creating, user needs creating but doesn't create
        """
        # User already exists
        dao = DaoMock()
        dao.results = [0, 1]  #So that will think user is inserted on checkuser step
        self.object.set_dao(dao)
        userid = "4567890"
        testdict = {'id': userid, 'test0': 'test0val', 'test1': 'test1val'}
        result = self.object.recordUser(testdict)
        self.assertTrue(result)

    def test_recordUser_goodCreation(self):
        """
        Currently impossible to test the second case because would have to have dao return different values to first get past checkuser 
        """
        # dao = DaoMock()
        #dao.results = ''
        #self.object.set_dao(dao)
        #userid = "4567890"
        #testdict = {'id' : userid, 'test0' : 'test0val', 'test1' : 'test1val'}
        #result = self.object.recordUser(testdict)
        #self.assertTrue(result)
        #self.assertEqual(len(dao.log), 6)
        pass

    def test_recordUser_throwsErrors(self):
        """
        @todo error handling tests
        """
        dao = DaoMock()
        dao.results = ''
        self.object.set_dao(dao)
        # self.assertRaises(UserServiceError, self.object.recordUser({'id':'j'}))
        pass

if __name__ == '__main__':
    unittest.main()