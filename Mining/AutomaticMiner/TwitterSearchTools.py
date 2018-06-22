"""
The soon-to-be-working tweet searcher
Formerly known as TwitterSearcher3.py
"""

from time import sleep
from Mining.Errors.ErrorClasses import *
from Mining.ProcessingTools import TweetDataProcessors


class Search:
    """
    Does the searching. Uses an observer to store and process results
    
    Attributes:
        MAX_PAGES:
        _observers: A list of observer objects
        twitter_conn: Twitter connection
        redis: RedisTools.RedisService object
        tweets: List that will contain TwitterDataProcessors.Tweet objects
    """

    def __init__(self):
        self.MAX_PAGES = 10
        self._observers = []
        self.tweets = []
        self.tweet_factory = TweetDataProcessors.TweetFactory()

    def attach_observer(self, observer):
        """
        This attaches an observer object which has an update method to be called when there are new tweets to be stored
        
        Args:
            observer: TweetSaverService.SearchObserver instance to be registered
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def detach_observer(self, observer):
        """
        Removes an attached observer object
        
        Args:
            observer: TweetSaverService.SearchObserver instance to be removed from registration
        """
        try:
            self._observers.remove(observer)
        except:
            raise ObserverError(observer)

    def notify_observers(self, modifier=None):
        for observer in self._observers:
            if modifier != observer:
                observer.update(self)

    def set_twitter_connection(self, login, credentials):
        """
        Args:
            credentials: String location of twitter credentials file
            login: TwitterLogin.login
        """
        self.twitter_conn = login(credentials)

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

    def set_logger(self, logger):
        """
        Args:
            logger Instance of Loggers.SearchLogger
        """
        self.logger = logger

    def run(self, list_of_search_terms, limit, recent=True, rest=800):
        """
        Performs the search. This version internalizes the timeout functions so that it only grabs the newest tweet once per search term list

        TODO Revise so that the only checks the starting tweet id once per group of query terms
        
        Args:
            list_of_search_terms: A list of the terms for the query to send to twitter
            limit: Integer representing the maximum number of times to run the search loop
            recent: Boolean True search for tweets newer than most recent record; False search for tweets older than oldest record
            rest: Integer of the time to rest in between searches
        """
        # Query
        self.search_terms = list_of_search_terms
        self.recent = recent
        # self.limitTweet = 100001
        self.limitTweet = self._get_starting_tweet(recent)

        run_number = 0
        while run_number <= limit:
            self.tweets = []
            self.logger.run_start(run_number)
            self.logger.limit_tweet(self.limitTweet, self.recent)
            idx = 0
            # Run the search for each of the search terms
            for term in self.search_terms:
                hashtag = '#%s' % term
                self.logger.search_term(term)
                search_results = self._search_twitter(hashtag, recent)
                # search_twitter returns a list of dicts (one for each page),
                # so iterate through those to process and consolidate tweets
                if len(search_results) > 0:
                    newtweets = []
                    for results in search_results:
                        newtweets += self._process_search_results(results)
                    self.tweets += newtweets
                    self.logger.number_of_results(term, len(newtweets))
                else:
                    self.logger.number_of_results(term, 0)
            self.notify_observers()
            # Rest before another run through all the search terms
            if idx % 2 == 0:
                self.logger.rest_start()
                sleep(rest)
            idx += 1
            run_number += 1

    def _get_oldest_tweet(self):
        """
        Handles interface with service class so don't have to change other things if use redis or mysql
        TODO Replace with redis search
        """
        return self.redis.get_oldest_id()

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

        Args:
            hashtag: Properly formatted string to search for
            recent: Boolean of whether to get recent tweets

        Returns:
            Returns a list of dictionaries from searches

        Raises:
            SearchError
        """
        search_results = []
        try:
            # Iterate the search for the current hashtag up to the maximum number of pages
            for _ in range(self.MAX_PAGES - 1):  # Get more pages
                if recent is False:  # search for older tweets
                    result = self.twitter_conn.search.tweets(q=hashtag, count=100,
                                                             max_id=self.limitTweet)  # tweets before ealiest record
                    search_results.append(result)
                elif recent is True:  # search for newer tweets
                    result = self.twitter_conn.search.tweets(q=hashtag, count=100,
                                                             since_id=self.limitTweet)  # get most recent tweets
                    search_results.append(result)
        except SearchError('_search_twitter') as e:
            print(e)
        finally:
            return search_results

    @staticmethod
    def _handle_id_field(tweet):
        """
        Update the tweet's id field to id_str to ensure uniqueness
        """
        tweetid = tweet['id_str']
        tweet['_id'] = tweetid
        return tweet

    def _process_search_results(self, search_results):
        """
        Handle tweet formatting of search results and put tweets into list

        Args:
            search_results: Dictionary from twitter search with tweets stored in search_results['statuses']

        Returns:
            List of TwitterDataProcessors.Tweet objects. The list will be empty if there was an error

        Raises:
            SearchError
        """
        tweets = []
        try:
            statuses = search_results['statuses']  # This is the list returned which contains all the tweets
            for tweet in statuses:
                tweet = self._handle_id_field(tweet)
                tweetobj = self.tweet_factory.make_tweet(tweet)
                tweets.append(tweetobj)
        except SearchError('_process_search_results') as e:
            print(e)
            pass
        finally:
            return tweets


"""
def newsearch:
self.search_results = self.twitter_conn.search.tweets(q=self.query, count=100)
"""

if __name__ == '__main__':
    pass