__author__ = 'ars62917'
"""
Tests for MySQLTools which run against a sqlite database
"""
import unittest

from SQL_UnitTestingTools import *

#from DaoMocks import *
from TwitterProjectTestEntities import *
from DatabaseTools.MySQLTools import *
from Mining.DatabaseAccessObjects import TestingCredentials
from Mining.ProcessingTools.TweetDataProcessors import *


class HashtagServiceTest(unittest.TestCase):
    def setUp(self):
        self.dao = TestingDao()
        self.dao.make_tables()
        self.credentials = TestingCredentials()
        self.object = HashtagService()

        self.object.set_dao(self.dao)
        self.object.set_helper(TagHelpers())
        self.tweetid = 1245678964
        self.tagid = 1235665433
        self.tagtext = 'fakeTag'
        self.formatted_tagtext = 'faketag'
        self.testags = [{'tagid': 1235665433, 'inputtext': 'TestTag0', 'formattedtext': 'testtag0'},
                        {'tagid': 1235665434, 'inputtext': 'TestTag1', 'formattedtext': 'testtag1'},
                        {'tagid': 1235665435, 'inputtext': 'TestTag2', 'formattedtext': 'testtag2'}]
        # Make fixture
        for t in self.testags:
            query = """INSERT INTO hashtags (tagID, hashtag) VALUES ('%s', '%s')""" % (t['tagid'], t['formattedtext'])
            print query
            self.dao.cursor.execute(query)
            self.dao.conn.commit()

    def tearDown(self):
        self.object.dao = ''
        self.dao = ''

    def test_getTagID(self):
        pass
        # for t in self.testags:
        #     result = self.object.getTagID(t['inputtext'])
        #     self.assertEqual(result, t['tagid'])

        # def test__recordTagText(self):
        #     self.object.taghelper = TagHelpers()
        #     self.object._recordTagText(self.tagtext)
        #     self.assertEqual(self.dao.log[0]['word_map_table_creation_query'], "INSERT INTO hashtags (hashtag) VALUES (%s)")
        #     self.assertEqual(self.dao.log[0]['val'], [self.tagtext.lower()])
        #     self.assertEqual(self.dao.log[0]['command'], 'executeQuery')

        # def test__recordTagAssoc(self):
            # self.object._recordTagAssoc(self.tweetid, self.tagid)
            # self.assertEqual(self.dao.log[0]['word_map_table_creation_query'], "INSERT IGNORE INTO tweetsXtags (tweetID, tagID) VALUES (%s, %s)")
            # self.assertEqual(self.dao.log[0]['val'], [self.tweetid, self.tagid])
            # self.assertEqual(self.dao.log[0]['command'], 'executeQuery')


if __name__ == '__main__':
    unittest.main()
