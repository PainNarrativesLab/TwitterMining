"""
Unit tests for test_twitterdataprocessors
"""
import unittest

from Mining.ProcessingTools.TweetDataProcessors import *
from tests.TwitterProjectTestEntities import *


taglist = ('tag1', 'tag2', 'tag3', 'tag4')
# expected_pairs = [('tag1', 'tag2'), ('tag1', 'tag3'), ('tag1', 'tag4'), ('tag2', 'tag3'), ('tag2', 'tag4'), ('tag3', 'tag4')]
#('tag4', 'tag1'), ('tag4', 'tag2'), ('tag4', 'tag3')]
expected_pairs = [('tag4', 'tag1'), ('tag4', 'tag2'), ('tag4', 'tag3'), ('tag1', 'tag2'), ('tag1', 'tag3'),
                  ('tag2', 'tag3')]


class TagHelpersTest(unittest.TestCase):
    def setUp(self):
        self.object = TagHelpers()

    def tearDown(self):
        self.object = ''

    def test_HTMLEntitiesToUnicode(self):
        testtags = ('ALLUPPER', 'miXeDcaseTag')
        expected = ('ALLUPPER', 'miXeDcaseTag')
        for i in range(0, len(testtags)):
            result = self.object.HTMLEntitiesToUnicode(testtags[i])
            self.assertEqual(result, expected[i])

    def test_format(self):
        testtags = ('ALLUPPER', 'miXeDcaseTag')
        expected = ('allupper', 'mixedcasetag')
        for i in range(0, len(testtags)):
            result = self.object.format(testtags[i])
            print(result)
            self.assertEqual(result, expected[i])

    def test_getHashtags(self):
        # testtags = ['tag1', 'tag2', 'tag3']
        #testrecord = {'entities' : {'hashtags' : {'text' : testtags[0], 'text' : testtags[1], 'text' : testtags[2]}}}
        result = self.object.getHashtags(test_tweet)
        self.assertEqual(result, EXPECTED_TAGS)
        #self.assertEqual(result, testrecord)


class TweetFactoryTest(unittest.TestCase):
    def setUp(self):
        self.object = TweetFactory()

    def tearDown(self):
        pass

    def test_make_tweet(self):
        pass

    def test__set_raw(self):
        self.object._set_raw(test_tweet)
        self.assertEqual(self.object.raw, test_tweet)

    def test__make_tweet(self):
        self.object.raw = test_tweet
        self.object._make_tweet()
        self.assertIsInstance(self.object.tweet, Tweet)
        self.assertEqual(self.object.raw, test_tweet)

    def test__process_hashtags(self):
        self.object.extractors = Extractors()
        self.object.tweet = Tweet()
        self.object.raw = test_tweet
        self.object._process_hashtags()
        self.assertEqual(self.object.tweet.hashtags, EXPECTED_TAGS)

    def test__process_user(self):
        self.object.tweet = Tweet()
        self.object.raw = test_tweet
        self.object._process_user()
        self.assertEqual(self.object.tweet.user, USER_DICT['user'])

    def test__process_text(self):
        self.object.tweet = Tweet()
        self.object.raw = test_tweet
        self.object._process_text()
        self.assertEqual(self.object.tweet.tweet_text, EXPECTED_TEXT)


class ExtractorsTest(unittest.TestCase):
    def setUp(self):
        self.object = Extractors()

    def tearDown(self):
        self.object = ''

    def test_getEntities(self):
        result = Extractors.getEntities(test_tweet)
        for r in result['hashtags']:
            self.assertIn(r['text'], EXPECTED_TAGS)

            # def test_extractHashtags(self):
            #   result = Extractors.extractHashtags(test_tweet)
            #   self.assertEqual(result, EXPECTED_TAGS)


class TagsFromSearchTest(unittest.TestCase):
    def setUp(self):
        self.object = TagsFromSearch()

    def tearDown(self):
        self.object = ''

    def test_getPairs(self):
        self.assertIsNotNone(test_tweet)
        result = self.object.getPairs(taglist)


class TagsTest(unittest.TestCase):
    def setUp(self):
        self.object = Tags()
        self.taglist = []

    def tearDown(self):
        self.object = ''

    def test_getPairs(self):
        self.result = Tags.getPairs(taglist)
        print(self.result)
        for p in self.result:
            self.assertIn(p, expected_pairs)
        for p in expected_pairs:
            self.assertIn(p, self.result)


if __name__ == '__main__':
    unittest.main()