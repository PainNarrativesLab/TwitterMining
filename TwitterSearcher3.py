# The working tweet searcher
import sys
import twitter
import couchdb
from couchdb.design import ViewDefinition

from TwitterUtilities import makeTwitterRequest
from TwitterLogin import login

from TwitterServiceClasses import CouchService
from TwitterServiceClasses import RedisService

from TwitterDataProcessors import Extractors

import datetime
from datetime import datetime
from time import sleep


class Search:
    """
    Does the searching
    """
    def __init__(self):
        self.MAX_PAGES = 10
        self._observers = []
    
    def attach_observer(self, observer):
        """
        This attaches an observer object which has an update method to be called when there are new tweets to be stored
        """
        if not observer in self._observers:
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


    def set_twitter_connection(self, login):
        """
        TwitterLogin.login
        """
        self.twitter_conn = login()
    
    def set_redis_service(self, RedisService):
        self.redis = RedisService
    
    def set_couch_service(self, CouchService):
        """
        self.DB_NAME = 'compiled'
        #connect
        try:
            CouchService.__init__(self, self.DB_NAME)
        except Exception as e:
            print 'Problem connecting to couchdb database: %s', e           
        CouchService.__init__(self, self.DB_NAME)
        """
        self.couch = CouchService
    
    def set_logger(self, Logger):
        """
        Instance of Loggers.SearchLogger
        """
        self.logger = Logger
        

    def run(self, list_of_search_terms, limit, recent=True, rest=800):
        """
        Performs the search. This version internalizes the timeout functions so that it only grabs the newest tweet once per search term list
        @param list_of_search_terms The query to send to twitter
        @type list_of_search_terms list
        @param limit The number of times to run the search loop
        @type limit int
        @param recent 'True' search for tweets newer than most recent record; 'False' search for tweets older than oldest record
        @type recent string
        @param rest The time to rest in between searches
        @type rest int
        @todo Revise so that the only checks the starting tweet id once per group of query terms
        """
        #Query
        self.search_terms = list_of_search_terms
        self.recent = recent
        self.tweets = []
        self.limitTweet = 100001
        #limitTweet = self._get_starting_tweet(recent)
        self.logger.limit_tweet(self.limitTweet, recent)

        run_number = 0
        while run_number <= limit:
            self.logger.run_start(run_number)
            idx = 0
            #Run the search for each of the search terms    
            for s in self.search_terms:
                hashtag = '#%s' % s
                self.logger.search_term(s)
                search_results = self._search_twitter(hashtag, recent)
                #search_twitter returns a list of dicts (one for each page), so iterate through those to process and consolidate tweets
                if len(search_results) > 0:
                    newtweets = []
                    for results in search_results:
                        newtweets += self._process_search_results(results)
                    self.tweets += newtweets
                    self.logger.number_of_results(s, len(newtweets))
                else:
                    self.logger.number_of_results(s, 0)
            #Rest before another run through all the search terms
            if idx % 2 == 0:
                self.logger.rest_start()
                sleep(rest)
            idx += 1
            run_number += 1
    
    def _get_oldest_tweet(self):
        """
        Handles interface with service class so don't have to change other things if use redis or mysql
        """
        return self.redis.get_oldest_id() #@todo Replace with redis search
    
    def _get_newest_tweet(self):
        self.redis.get_max_id()
        return self.redis.maxid
    
    def _get_starting_tweet(self, recent):
        """
        Get tweetid to start from or to stop at. This is done here so that will only happen once per loop through search terms
        """
        limitTweet = None
        if recent is False:
            limitTweet = self._get_oldest_tweet()
        elif recent is True:
            limitTweet = self._get_newest_tweet()
        return limitTweet

    def _search_twitter(self, hashtag, recent):
        """
        This searches twitter for the specified hashtag
        @param hashtag Properly formatted string to search for
        @type hashtag String
        @param recent Whether to get recent tweets
        @type recent Boolean
        @returns list List of dictionaries from searches
        """
        try:            
            search_results = []
            ##Iterate the search for the current hashtag up to the maximum number of pages
            for _ in range(self.MAX_PAGES-1):  # Get more pages
                if recent == False: #search for older tweets
                    result = self.twitter_conn.search.tweets(q=hashtag, count=100, max_id=self.limitTweet) #tweets before ealiest record
                    search_results.append(result)
                elif recent == True: #search for newer tweets
                    result = self.twitter_conn.search.tweets(q=hashtag, count=100, since_id=self.limitTweet) #get most recent tweets
                    search_results.append(result)
        except Exception as e:
            #pass
            #TODO Add exception handling
            print 'Error in twitter searching: %s' % e
        finally:
            return search_results

    def _handle_id_field(self, tweet):
        """
        Update the tweet's id field to id_str to ensure uniqueness
        """
        tweetid = tweet['id_str']
        tweet['_id'] = tweetid
        return tweet
    
    def _process_search_results(self, search_results):
        """
        Handle tweet formatting of search results and put tweets into list
        @param search_results Dictionary from twitter search with tweets stored in search_results['statuses']
        @type search_results Dictionary
        @returns list List of tweets
        """
        statuses = search_results['statuses']  # This is the list returned which contains all the tweets
        tweets = []
        try:
            for tweet in statuses:
                tweet = self._handle_id_field(tweet)
                tweets.append(tweet)
        except Exception as e:
            print 'Error with _process_search_results'
            #add handling
        finally:
            return tweets
     


"""
def newsearch:
self.search_results = self.twitter_conn.search.tweets(q=self.query, count=100)
"""
