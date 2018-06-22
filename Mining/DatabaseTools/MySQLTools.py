"""
These are service classes for saving the various components of tweets to a mysql database

Depends:
    While doesn't explicitly import, these classes load and call the following:
        TwitterSQLService.SQLService
        TwitterDataProcessors.TagHelpers
        TwitterDataProcessors.Formatter

TODO: Better error handling.
TODO: Maybe get all ids then transfer one by one
"""

from ErrorClasses import *


class TwitterMySqlServiceParent(object):
    """
    Common parent for all classes which save twitter objects to mysql database

    Attributes:
        dao: TwitterSQLService.SQLService object which handles db interactions
        helper: TwitterDataProcessors.TagHelpers or TwitterDataProcessors.Formatter
    """
    def __init__(self):
        pass

    def set_dao(self, dao):
        """
        Loads the object which handles db interaction

        Args:
            dao: TwitterSQLService.SQLService object
        """
        self.dao = dao

    def set_helper(self, helper):
        """
        Load in an instance of TwitterDataProcessors.Formatter or one of its children for formatting etc

        Args:
            helper: TwitterDataProcessors.Formatter or child
        """
        self.helper = helper


class TweetService(TwitterMySqlServiceParent):
    """
    Accesses the tweet mysql database to record tweet data.
    Upon initialization, must do:
        set_dao()
        set_helper()
    before ready to run.
    
    Attributes:
        dao: TwitterSQLService.SQLService object which handles db interactions
        helper: TwitterDataProcessors.TagHelpers or TwitterDataProcessors.Formatter
    """
    def __init__(self):
        TwitterMySqlServiceParent.__init__(self)

    def recordTweetData(self, tweetID, tweet):
        """
        Records a tweet text to the mysql db
        
        Args:
            tweetID: String tweetid ID of the tweet from the id_str field
            tweet: TwitterDataProcessors.Tweet object
        
        Raises:
            TweetServiceError: Raised when there is an error processing the tweet text or inserting into the db
        TODO: Make sure user id is recorded before attempting
        TODO: Rewrite to take a TwitterServiceClasses.Tweet object as input
        """
        try:
            text = self.helper.HTMLEntitiesToUnicode(tweet.tweet_text)
            self.dao.query = """INSERT IGNORE INTO tweets (tweetID, tweetText, userID, lang, created_at)
             VALUES (%s, %s, %s, %s, %s)"""
            self.dao.val = [tweetID, text, tweet.userID, tweet.raw_tweet['lang'], tweet.raw_tweet['created_at']]

            #
            # text = self.helper.HTMLEntitiesToUnicode(tweet.tweet_text)
            # #            text = self.HTMLEntitiesToUnicode(tweet['text'])
            # self.dao.query = """INSERT IGNORE INTO tweets (tweetID, tweetText, favorite_count, source, retweeted,
            # in_reply_to_screen_name, retweet_count, favorited, userID, lang, created_at)
            #  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            # self.dao.val = [tweetID, text,
            #                 tweet.raw_tweet['favorite_count'], tweet.raw_tweet['source'],
            #                 tweet.raw_tweet['retweeted'], tweet.raw_tweet['in_reply_to_screen_name'],
            #                 tweet.raw_tweet['retweet_count'], tweet.raw_tweet['favorited'],
            #                 tweet.raw_tweet['user']['id'], tweet.raw_tweet['lang'], tweet.raw_tweet['created_at']]
            self.dao.executeQuery()
        except TweetServiceError(tweetID):
            pass


class HashtagService(TwitterMySqlServiceParent):
    """
    Handles getting and recording hashtags to mysql database
    Upon initialization, must do:
        set_dao()
        set_taghelper()
    before ready to run.

    Attributes:
        dao: TwitterSQLService.SQLService object which handles db interactions
        helper: TwitterDataProcessors.TagHelpers object
    """

    def __init__(self):
        TwitterMySqlServiceParent.__init__(self)

    def getTagID(self, tagText):
        """
        Retrieves the unique identifier for a given hashtag
        
        Args:
            tagText: String text of the hashtag to get

        Returns:
            Returns a dictionary with key tagID containing the id string of the hashtag
        """
        tag = self.helper.format(tagText)
        if tag is not None:
            self.dao.query = """SELECT tagID FROM hashtags WHERE hashtag = %s"""
            self.dao.val = [tag]
            self.dao.returnOne()
            return self.dao.results

    def _recordTagText(self, tagText):
        """
        Records the tag text for new tags
        
        Args:
            tagText: String of the hashtag to be recorded
        """
        tag = self.helper.format(tagText)
        if tag is not None:
            self.dao.query = """INSERT IGNORE INTO hashtags (hashtag) VALUES (%s)"""
            self.dao.val = [tag]
            self.dao.executeQuery()
        # return self.dao.returnInsertID()

    def _recordTagAssoc(self, tweetID, tagID):
        """
        Associates a tag with a tweet in the db.
        
        Args:
            tweetID: ID of the tweet to be associated
            tagID: ID of the tag to be associated
        """
        self.dao.query = """INSERT IGNORE INTO tweetsXtags (tweetID, tagID) VALUES (%s, %s)"""
        self.dao.val = [tweetID, tagID]
        self.dao.executeQuery()

    def recordHashtags(self, tweetID, tags):
        """
        Records hashtags to database

        Args:
            tweetid: Integer ID of the tweet from id_str
            tags: List of tag strings
        
        Raises:
            HashtagServiceError: Raised on error, contains tweetID
        """
        assert not isinstance(tags, str)
        for tag in tags:
            try:
                self._recordTagText(tag)
                tagID = self.getTagID(tag)
                if tagID is not None:
                    self._recordTagAssoc(tweetID, tagID['tagID'])
                # Lookup tag id
                # tagID = self.getTagID(tag)
                # if tagID is None:
                #     # Insert the tag text into hashtags table
                #     tagID = self._recordTagText(tag)
                #     # tagID = self.getTagID(tag)
                # if tagID is not None:  # Now have id. Make association
                #     self._recordTagAssoc(tweetID, tagID['tagID'])
            except HashtagServiceError(tweetID):
                pass


class UserService(TwitterMySqlServiceParent):
    """
    Handles db interactions for tweet user
    Needs to run set_dao() before ready to go
    
    Attributes:
        dao: TwitterSQLService.SQLService object which handles db interactions
        helper: TwitterDataProcessors.TagHelpers or TwitterDataProcessors.Formatter
        ignorecolumns: List of columns from tweet that will not be recorded in mysql db
    """

    def __init__(self):
        TwitterMySqlServiceParent.__init__(self)
        self.ignorecolumns = ['id', 'entities',
                              'follow_request_sent',
                              'profile_use_background_image',
                              'profile_text_color',
                              'profile_image_url_https',
                              'profile_sidebar_fill_color',
                              'is_translator',
                              'geo_enabled',
                              'protected',
                              'default_profile_image', 'profile_link_color', 'profile_image_url', 'notifications',
                              'profile_background_image_url_https', 'profile_background_color', 'profile_banner_url',
                              'profile_background_image_url', 'profile_background_tile', 'contributors_enabled',
                              'profile_sidebar_border_color', 'default_profile', 'following', 'listed_count',
                              'follow_request_sent']

    def _filter_userDict(self, userDict):
        to_use = [x for x in userDict.keys() if x not in self.ignorecolumns]
        return to_use

    def check_user(self, userID):
        """
        Used to check whether user already exists
        
        Args:
            userID: Id of user to check in db
        
        Returns:
            Boolean True or False indicating whether the user is already record
        """
        self.dao.query = """SELECT userID FROM users WHERE userID = %s"""
        self.dao.val = [userID]
        self.dao.returnAll()
        if len(self.dao.results) > 0:
            return True
        else:
            return False

    def _add_user_to_user_table(self, userID):
        """
        Inserts userID into table prior to updating the various fields
        
        Args:
            userID: Id of user to insert
        """
        self.dao.query = """INSERT INTO users (userID) VALUES (%s)"""
        self.dao.val = [userID]
        self.dao.executeQuery()

    def _update_user_table_fields(self, userID, fields_to_update, userDict):
        """
        Once the user is in the users table, fill the various fields with properties of the user
        
        Args:
            userID: Id of user
            fields_to_update: List of fields in users table to update
            userDict: Dictionary with keys corresponding to columns in the users table
        """
        for k in fields_to_update:
            self.dao.query = """UPDATE users SET %s = %%s WHERE userID = %%s""" % k
            self.dao.val = [userDict[k], userID]
            self.dao.executeQuery()

    def createUser(self, userDict):
        """
        Creates a new user record. Only necessarily does useriD
        
        Args:
            userDict: Dictionary containing user info
        
        Raises:
            UserServiceError
        """
        # Insert the userID
        self._add_user_to_user_table(userDict['id'])
        # Make sure inserted
        if self.check_user(userDict['id']) is True:
            # Filter the fields to insert
            self.fields_to_update = self._filter_userDict(userDict)
            self._update_user_table_fields(userDict['id'], self.fields_to_update, userDict)
        else:
            raise UserServiceError(userDict['id'])

    def recordUser(self, userDict):
        """
        First checks whether the user is already in the database, if not creates user.
        This should be the primarily called method
        
        Args:
            userDict: Dictionary containing user info
        
        Raises:
            UserServiceError
        """
        if self.check_user(userDict['id']):
            return True
        else:
            self.createUser(userDict)
            if self.check_user(userDict['id']):
                return True
            else:
                raise UserServiceError(userDict['id'])


if __name__ == '__main__':
    pass