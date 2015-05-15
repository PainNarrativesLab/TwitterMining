# Twitter specific
import itertools  # For set operations

import twitter_text  # easy_install twitter-text-py
from BeautifulSoup import BeautifulStoneSoup
from ErrorClasses import *


class Tweet(object):
    """
    Data holder object. This is the object all recorders will expect to receive.
    So the usual workflow is to take tweets scraped from twitter or loaded from the database. And push them into
    one of these objects to be properly formatted etc

    Attributes:
        tweetID: The string identifier of the tweet
        hashtags: A list of hashtags present in the tweet
        raw_tweet: String of the entire tweet entity captured
        tweet_text: String of the text of the tweet in unicode
        user: Dictionary with information about user
    """

    def __init__(self):
        self.tweetID = ''
        self.userID = ''
        self.hashtags = []
        self.raw_tweet = ''
        self.tweet_text = ''
        self.user = dict()

    def set_tweetID(self, tweetID):
        self.tweetID = tweetID

    def set_userID(self, userID):
        self.userID = userID

    def set_hashtags(self, list_of_hashtags):
        self.hashtags += list_of_hashtags

    def set_raw_tweet(self, raw_tweet):
        self.raw_tweet = raw_tweet

    def set_text(self, tweet_text):
        self.tweet_text = tweet_text

    def set_user_info(self, user_dict):
        for k in user_dict.keys():
            self.user[k] = user_dict[k]


class Formatter(object):
    """
    Helps convert items found in tweets into proper formats
    """

    def __init__(self):
        pass

    def HTMLEntitiesToUnicode(self, text):
        """
        Converts HTML entities to unicode.  For example '&amp;' becomes '&'.
        Args:
            text: HTML laden text to convert to unicode
        Returns:
            String converted to unicode
        """
        try:
            text = unicode(BeautifulStoneSoup(text, convertEntities=BeautifulStoneSoup.ALL_ENTITIES))
            return text
        except Exception as e:
            print "error formatting string: %s ; Errors:  %s" % text, e
            return None

    def format(self, text):
        """
        Transforms to unicode and casts as string
        """
        try:
            txt = self.HTMLEntitiesToUnicode(text)
            # txt = str(txt)
            return txt
        except Exception as e:
            print "error formatting string: %s ; Errors:  %s" % text, e
            return None


class Extractors(object):
    """
    These process the raw tweet for specific components
    Wrapper for twitter_text.Extractor
    """
    def __init__(self):
        pass

    def get_entities(self, tweet):
        return Extractors.getEntities(tweet)

    @staticmethod
    def getEntities(tweet):
        # Now extract various entities from it and build up a familiar structure
        extractor = twitter_text.Extractor(tweet['text'])
        # Note that the production Twitter API contains a few additional fields in
        # the entities hash that would require additional API calls to resolve
        entities = {}
        entities['user_mentions'] = []
        for um in extractor.extract_mentioned_screen_names_with_indices():
            entities['user_mentions'].append(um)
        entities['hashtags'] = []
        for ht in extractor.extract_hashtags_with_indices():
            # massage field name to match production twitter api
            ht['text'] = ht['hashtag']
            del ht['hashtag']
            entities['hashtags'].append(ht)
        entities['urls'] = []
        for url in extractor.extract_urls_with_indices():
            entities['urls'].append(url)
        return entities

    @staticmethod
    def extractHashtags(searchresult):
        """
        Gets hashtags from a twitter search result
        @param searchresult A JSON twitter search result
        @param string
        @returns List of tags in search
        """
        try:
            all_tags_from_search = []  # holds all tags from search
            statuses = searchresult['statuses']  # list of statuses from search
            # cycle through each status
            for status in statuses:
                record = []  # list to hold all hashtags from this status
                entities = Extractors.getEntities(status)
                list_of_hashtags = entities['hashtags']
                for tag in list_of_hashtags:
                    record.append(tag['text'])
                all_tags_from_search.append(record)
                return all_tags_from_search
        except Exception as e:
            print 'Error in hashtag extraction %s' % e


class TweetFactory(Formatter, Extractors):
    """
    This takes raw tweets and makes the expected tweet object
    Needs to run set_extractors() before ready to go.

    Attributes:
        extractors: TwitterDataProcessors.Extractors
    """
    def __init__(self):
        Formatter.__init__(self)
        Extractors.__init__(self)

    # def set_extractors(self, extractors=None):
    #     """
    #     Loads in an object which handles extracting tweet entities. Checks if a custom
    #     extractor was passed in, if not sets the default TwitterDataProcessors.Extractors
    #
    #     Args:
    #         extractors: TwitterDataProcessors.Extractors
    #     """
    #     if extractors is not None:
    #         self.extractors = Extractors
    #     else:
    #         self.extractors = Extractors()

    # def _check_extractors_set(self):
    #     """
    #     Checks whether extractor has been set, if not, sets to default
    #     """
    #     self.extractors = TweetDataProcessors.Extractors()
    #     # if not self.extractors:
    #     #     self.set_extractors()

    def make_tweet(self, raw_tweet):
        """
        This is the main publically called method
        """
        self.tweet = Tweet()
        self.tweet.set_tweetID(raw_tweet['id_str'])
        uid = raw_tweet['user']['id_str']
        self.tweet.set_userID(uid)
        # self._check_extractors_set()
        self._set_raw(raw_tweet)
        self._process_hashtags()
        self._process_user()
        self._process_text()
        return self.tweet

    def _set_raw(self, tweet):
        """
        Sets the input to self.raw. Everything should operate off of self.raw
        """
        self.raw = tweet
        self.tweet.set_raw_tweet(tweet)

    def _make_tweet(self):
        pass
        # self.tweet.set_raw_tweet(self.raw)

    def _process_hashtags(self):
        # tags = self.extractors.extractHashtags(self.raw)
        result = self.get_entities(self.raw)
        tags = [self.format(r['text']) for r in result['hashtags']]
        if len(tags) > 0:
            self.tweet.set_hashtags(tags)

    def _process_user(self):
        self.tweet.set_user_info(self.raw['user'])

    def _process_text(self):
        self.tweet.set_text(self.raw['text'])


class TagHelpers(Formatter):
    """
    This contains tools for working with hashtags.
    It handles formatting hashtags as well as extracting them from the tweet
    """
    def __init__(self):
        Formatter.__init__(self)

    def format(self, tagText):
        """
        Make the appropriate transformations to the hashtag
        """
        try:
            tag = self.HTMLEntitiesToUnicode(tagText)
            # tag_d = tag.decode('utf-8')
            # tag_d = str(tag_d)
            tag = tag.lower()
            return tag
        except HashtagTextError(tagText):
            pass
            # finally:
            # return tagText
            # print "Tag formatting failed for tag text: %s \n %s" % (tagText, e)

    def getHashtags(self, record):
        """Extracts hashtags from the record

        Args:
            record: Dictionary with key 'entities' which holds a dictionary with the key 'hashtags'

        Returns:
            hashtags: List of hashtags present in the record
        """
        hashtags = []
        for r in record['entities']['hashtags']:
            hashtags.append(r['text'])
        return hashtags


class TagsFromSearch(object):
    def __init__(self):
        self.pairs = []  # Holds tuples
        self.alltags = []  # Holds a raw list of all tags, to be counted by something else later

    def getPairs(self, list_of_lists_of_tags):
        """
        Returns a list of tuples from a list of listsw
        """
        for t in list_of_lists_of_tags:
            # Alphabetize
            #t = t.sort()
            #lowercase all
            #t = [w.lower() for w in t]
            #collect all tags for frequency analysis later
            [self.alltags.append(i) for i in t]
            #For each list, first get the set
            set_of_terms = set(t)

            #Then get all the proper subsets of length 2 from s
            ps = itertools.combinations(set_of_terms, 2)
            for p in ps:
                if p != set():
                    self.pairs.append(p)
        return self.pairs, self.alltags


class Tags(object):
    @staticmethod
    def getPairs(list_of_tags):
        """
        Returns a list of tuples comprising the proper subsets length 2 of the list
        """
        pairs = []  # Holds tuples
        # alltags = [] #Holds a raw list of all tags, to be counted by something else later
        if len(list_of_tags) > 1:
            set_of_terms = set(list_of_tags)
            #Then get all the proper subsets of length 2 from s
            ps = itertools.combinations(set_of_terms, 2)
            for p in ps:
                if p != set():
                    pairs.append(p)
            return pairs
        else:
            return list_of_tags


if __name__ == '__main__':
    pass