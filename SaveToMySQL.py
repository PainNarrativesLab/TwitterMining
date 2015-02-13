#TODO: Better error handling. 
#TODO: Maybe get all ids then transfer one by one
import TwitterSQLService

from BeautifulSoup import BeautifulStoneSoup
from ErrorClasses import *
"""
class TweetError(Exception):
    def __init__(self, tweetID):
        self.tweetID = tweetID
    def __repr__(self):
        return "%s went bad on tweetID %s" % (self.kind, self.tweetID)

class TweetServiceError(TweetError):
    def __init__(self, tweetID):
        self.kind = 'TweetService'
        TweetError.__init__(self, tweetID)
        
class HashtagServiceError(TweetError):
    def __init__(self, tweetID):
        self.kind = 'HashtagService'
        TweetError.__init__(self, tweetID)

class UserServiceError(TweetError):
    def __init__(self, tweetID):
        self.kind = 'UserService'
        TweetError.__init__(self, tweetID)
"""

class TagHelpers(object):
    """
    This handles formatting hashtags as well as extracting them from the tweet
    """
    
    def HTMLEntitiesToUnicode(self, text):
        """
        Converts HTML entities to unicode.  For example '&amp;' becomes '&'.
        
        Args:
            text: The string to be converted to unicode
        """
        text = unicode(BeautifulStoneSoup(text, convertEntities=BeautifulStoneSoup.ALL_ENTITIES))
        return text
    
    def format(self, tagText):
        """
        Make the appropriate transformations to the hashtag
        """
        try:
            tag = self.HTMLEntitiesToUnicode(tagText)
            tag = str(tag)
            tag = tag.lower()
            return tag
        except:
            raise HashtagServiceError(tagText)
        #finally:
            #return tagText
            #print "Tag formatting failed for tag text: %s \n %s" % (tagText, e)
    
    def getHashtags(self, record):
        """
        Extracts hashtags from the record
        
        Args:
            record: Dictionary with key 'entities' which holds a dictionary with the key 'hashtags'
        
        Returns:
            hashtags: List of hashtags present in the record
        """
        hashtags = []
        for r in record['entities']['hashtags']:
            hashtags.append(r['text'])
        return hashtags


class TweetService(object):
    """
    Accesses the tweet mysql database to record tweet data
    
    Attributes:
        dao: TwitterSQLService.SQLService object which handles db interactions
        helper: Tag helper object 
    """
         
    def set_dao(self, dao):
        """
        Loads the object which handles db interaction
        
        Args:
            dao: TwitterSQLService.SQLService object
        """
        self.dao = dao
        
    def set_taghelper(self, helper):
        self.helper = helper
        
    def recordTweetData(self, tweetID, tweet):
        """
        Records a tweet to the mysql db
        
        Args:
            tweetID: String tweetid ID of the tweet from the id_str field
            tweet: String text of the tweet
        
        Raises:
            TweetServiceError: Raised when there is an error processing the tweet text or inserting into the db
        """
        ##Make sure user id is recorded
        try:
            #text = tweet['text']
            text = self.helper.HTMLEntitiesToUnicode(tweet['text'])
#            text = self.HTMLEntitiesToUnicode(tweet['text'])
            self.dao.query = """INSERT INTO tweets (tweetID, tweetText, favorite_count, source, retweeted, in_reply_to_screen_name, retweet_count, favorited, userID, lang, created_at)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            self.dao.val = [tweetID, text, 
                      tweet['favorite_count'], tweet['source'], 
                      tweet['retweeted'], tweet['in_reply_to_screen_name'], 
                      tweet['retweet_count'], tweet['favorited'], 
                      tweet['user']['id'], tweet['lang'], tweet['created_at']]
            self.dao.executeQuery()
        except:
            raise TweetServiceError(tweetID)
            #print "Error in recording tweet %s. \n %s" % (tweetID, e)


class HashtagService(TwitterSQLService.SQLService):
    """
    Handles db interactions for hashtags
    """
    def __init__(self, test=False, local=True):
        TwitterSQLService.SQLService.__init__(self, test, local)
    
    def set_dao(self, dao):
        """
        Load db interaction handler
        
        Args:
            dao: TwitterSQLService.SQLService object which handles db interactions.
        """
        self.dao = dao
    
    def set_taghelper(self, taghelper):
        """
        Load tag helper.
        
        Args:
            taghelper: Object which processes tags 
        """
        self.taghelper = taghelper
 
    def getTagID(self, tagText):
        """
        Retrieves the unique identifier for a given hashtag
        
        Args:
            tagText: String text of the hashtag to get
        Returns:
            Returns a dictionary with key tagID containing the id string of the hashtag
        """
        tag = self.taghelper.format(tagText)
        self.dao.query = """SELECT tagID FROM hashtags WHERE hashtag = %s"""
        self.dao.val = [tagText]
        self.dao.returnOne()
        return self.results

    def _recordTagText(self, tagText):
        """
        Records the tag text for new tags
        
        Args:
            tagText: String of the hashtag to be recorded
        """
        tag = self.taghelper.format(tagText)
        self.dao.query = """INSERT INTO hashtags (hashtag) VALUES (%s)"""
        self.dao.val = [tag]
        self.dao.executeQuery()
    
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
        Args:
            tweetid: Integer ID of the tweet from id_str
            tags: List of tag strings
        
        Raises:
            HashtagServiceError: Raised on error, contains tweetID
        """
        for tag in tags:
            try:
                #Lookup tag id
                tagID = self.getTagID(tag)
                if tagID == None:
                    #Insert the tag text into hashtags table
                    self.recordTagText(tag)
                    tagID = self.getTagID(tag)
                if tagID != None: #Now have id. Make association
                   self.recordTagAssoc(tweetID, tagID['tagID']) 
            except:
                raise HashtagServiceError(tweetID)
            #except Exception as e:
            #    print "Error in recording hashtags for tweetid %s. \n Tag: %s \n %s" % (tweetID, tag, e)    

class UserService(object):
    """
    Handles db interactions for tweet user
    
    Attributes:
        ignorecolumns: List of columns from tweet that will not be recorded in mysql db
    """
    def __init__(self):
        #TwitterSQLService.SQLService.__init__(self, test, local)
        self.ignorecolumns = ['id', 'entities',
        'follow_request_sent',
        'profile_use_background_image',
        'profile_text_color',
        'profile_image_url_https',
        'profile_sidebar_fill_color',
        'is_translator',
        'geo_enabled',
        'protected',
        'default_profile_image','profile_link_color', 'profile_image_url','notifications',
        'profile_background_image_url_https', 'profile_background_color','profile_banner_url',
        'profile_background_image_url', 'profile_background_tile','contributors_enabled',
        'profile_sidebar_border_color','default_profile', 'following','listed_count',
        'follow_request_sent']
    
    def set_dao(self, dao):
        """
        @param dao TwitterSQLService.SQLService
        """
        self.dao = dao

    def _filter_userDict(self, userDict):
        touse = [x for x in userDict.keys() if x not in self.ignorecolumns]
        return touse
    
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
        #Insert the userID
        self._add_user_to_user_table(userDict['id'])
        #Make sure inserted
        if self.check_user(userDict['id']) == True:
            #Filter the fields to insert
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
        if self.check_user(userDict['id']) == True:
            return True
        else:
            self.createUser(userDict)
            if self.check_user(userDict['id']) == True:
                return True
            else:
                raise UserServiceError(userDict['id'])
