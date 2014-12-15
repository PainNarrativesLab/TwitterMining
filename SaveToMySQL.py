#TODO: Better error handling. 
#TODO: Maybe get all ids then transfer one by one
import TwitterSQLService

from BeautifulSoup import BeautifulStoneSoup

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

class TagHelpers:
    """
    This handles formatting hashtags as well as extracting them from the tweet
    """
    
    def HTMLEntitiesToUnicode(self, text):
        """Converts HTML entities to unicode.  For example '&amp;' becomes '&'."""
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
        hashtags = []
        for r in record['entities']['hashtags']:
            hashtags.append(r['text'])
        return hashtags


class TweetService:
         
    def set_dao(self, dao):
        """
        @param TwitterSQLService.SQLService
        """
        self.dao = dao
        
    def set_taghelper(self, helper):
        self.helper = helper
        
    def recordTweetData(self, tweetID, tweet):
        """
        @param tweetid ID of the tweet from id_str
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
    def __init__(self, test=False, local=True):
        TwitterSQLService.SQLService.__init__(self, test, local)
    
    def set_dao(self, dao):
        """
        @param TwitterSQLService.SQLService.
        """
        self.dao = dao
    
    def set_taghelper(self, taghelper):
        """
        @param TagHelpers
        """
        self.taghelper = taghelper
 
    def getTagID(self, tagText):
        """
        Retrieves the identifier for a given hashtag
        @param The text of the hashtag to get
        """
        tag = self.taghelper.format(tagText)
        self.dao.query = """SELECT tagID FROM hashtags WHERE hashtag = %s"""
        self.dao.val = [tagText]
        self.dao.returnOne()
        return self.results

    def _recordTagText(self, tagText):
        """
        Records the tag text for new tags 
        """
        tag = self.taghelper.format(tagText)
        self.dao.query = """INSERT INTO hashtags (hashtag) VALUES (%s)"""
        self.dao.val = [tag]
        self.dao.executeQuery()
    
    def _recordTagAssoc(self, tweetID, tagID):
        """
        Associates a tag with a tweet
        """
        self.dao.query = """INSERT IGNORE INTO tweetsXtags (tweetID, tagID) VALUES (%s, %s)"""
        self.dao.val = [tweetID, tagID]
        self.dao.executeQuery()
        
    def recordHashtags(self, tweetID, tags):
        """
        @param tweetid int ID of the tweet from id_str
        @param tags list of tag strings
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

class UserService:
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
        """
        self.dao.query = """INSERT INTO users (userID) VALUES (%s)"""
        self.dao.val = [userID]
        self.dao.executeQuery()
    
    def _update_user_table_fields(self, userID, fields_to_update, userDict):
        """
        Once the user is in the table, fill the various fields
        """
        for k in fields_to_update:
            self.dao.query = """UPDATE users SET %s = %%s WHERE userID = %%s""" % k
            self.dao.val = [userDict[k], userID]
            self.dao.executeQuery() 
        
    
    def createUser(self, userDict):
        """
        Creates the user record. Only necessarily does useriD
        @param userDict Dictionary containing user info
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
        first checks whether the user is already in the database, if not creates user
        This should be the primarily called method
        """
        if self.check_user(userDict['id']) == True:
            return True
        else:
            self.createUser(userDict)
            if self.check_user(userDict['id']) == True:
                return True
            else:
                raise UserServiceError(userDict['id'])
