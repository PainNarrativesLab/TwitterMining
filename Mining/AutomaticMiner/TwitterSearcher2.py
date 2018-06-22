# The working tweet searcher
import sys
import datetime
from datetime import datetime
from time import sleep

import networkx as nx

from Mining.AccessManagement.TwitterLogin import login
from DatabaseTools.CouchDBTools import CouchService
from DatabaseTools.RedisTools import RedisService
from Mining.ProcessingTools.TweetDataProcessors import Extractors


class GraphBuilder:
    """
    This will add the tweets to a stored graph to save time in analyzing graphs later
    """

    def __init__(self):
        """
        @param tweetlist The list containing all the tweets
        """
        self.graphFile = 'tweet_hashtags_graph_MASTER.gexf'

    def load_graph(self):
        try:
            # load graph from file
            self.graph = nx.read_gexf(self.graphFile)
            # print 'Start graph info', nx.info(self.graph)
        except Exception as e:
            print 'Error loading graph from %s: %s' % (self.graphFile, e)
            # Prevent further execution
            sys.exit()

    def build_from_single_tweet(self, tweet):
        """
        This will save all the hashtags from a single tweet to the graph file
        """
        entities = Extractors.getEntities(tweet)
        if len(entities['hashtags']) >= 1:
            self.load_graph()
            try:
                list_of_hashtags = entities['hashtags']
                tweet_tuples = []
                # Format each of the hashtags and add the tuple
                for tag in list_of_hashtags:
                    tag_cleaned = str(tag['text'])
                    tag_cleaned = tag_cleaned.lower()
                    tweetid = tweet['id_str']
                    tweet_tuple = (tweetid, tag_cleaned)
                    tweet_tuples.append(tweet_tuple)
                try:
                    #Add tag to the graph. Done here so that one bad edge won't bring everything down
                    self.graph.add_edges_from(tweet_tuples)
                except Exception as e:
                    print 'Error adding edge for tweet id %s and hashtag %s. Details: %s' % (tweetid, tag_cleaned, e)
                #todo Add redis log of non recorded hashtags
            finally:  # record added edges
                nx.write_gexf(self.graph, self.graphFile)
            #	print 'Saved graph info : ', nx.info(self.graph)#for tweet in tweetObject:

    def from_tweet_list(self, tweetlist):
        """
        Used if need to record a list of tweets
        """
        try:
            for tweet in tweetlist:
                self.from_single_tweet(tweet)
        except Exception as e:
            print 'Error saving tweetlist %s' % e


class Search(CouchService, GraphBuilder):
    """
    Does the searching
    """

    def __init__(self, credentials_file):
        self.twitter_conn = login(credentials_file)
        self.redis_service = RedisService()
        GraphBuilder.__init__(self)
        self.DB_NAME = 'compiled'
        # connect
        try:
            CouchService.__init__(self, self.DB_NAME)
        except Exception as e:
            print 'Problem connecting to couchdb database: %s', e

    def run(self, list_of_search_terms, limit, recent='True', rest=800):
        """
        Performs the search. This version internalizes the timeout functions so that it only grabs the newest tweet once per search term list
        @param list_of_search_terms The word_map_table_creation_query to send to twitter
        @type list_of_search_terms list
        @param limit The number of times to run the search loop
        @type limit int
        @param recent 'True' search for tweets newer than most recent record; 'False' search for tweets older than oldest record
        @type recent string
        @param rest The time to rest in between searches
        @type rest int
        @todo Revise so that the only checks the starting tweet id once per group of word_map_table_creation_query terms
        """
        # Query
        self.search_terms = list_of_search_terms
        self.MAX_PAGES = 10
        self.recent = recent

        run_number = 0
        while run_number <= limit:
            print '------------------------------------------------------------------'

            print datetime.now()
            print "Run number: %d" % run_number
            idx = 0
            #Get tweetid to start from or to stop at. This is done here so that will only happen once per loop through search terms
            if self.recent == 'False':
                print 'Searching for older tweets....'
                self.get_oldest_id()  #@todo Replace with redis search
                self.limitTweet = self.oldest
            elif self.recent == 'True':
                print 'Getting newer tweets....'
                self.redis_service.get_max_id()
                self.limitTweet = self.redis_service.maxid
                print 'Newest stored tweet %s' % self.limitTweet
            #Run the search for each of the search terms
            for s in self.search_terms:
                hashtag = '#%s' % s
                self.search_twitter(hashtag)

            #Rest before another run through all the search terms
            if idx % 2 == 0:
                print 'resting'
                print datetime.now()
                sleep(rest)
            idx += 1
            run_number += 1

    def search_twitter(self, hashtag):
        """
        This searches twitter for the specified hashtag
        @param hashtag Properly formatted string to search for
        @type hashtag String
        """
        print 'Looking up %s' % hashtag
        try:
            ##Iterate the search for the current hashtag up to the maximum number of pages
            for _ in range(self.MAX_PAGES - 1):  # Get more pages
                if self.recent == 'False':  # search for older tweets
                    search_results = self.twitter_conn.search.tweets(q=hashtag, count=100,
                                                                     max_id=self.limitTweet)  #tweets before ealiest record
                    if len(search_results) > 0:
                        self.process_search_results(search_results['statuses'])
                elif self.recent == 'True':  # search for newer tweets
                    search_results = self.twitter_conn.search.tweets(q=hashtag, count=100,
                                                                     since_id=self.limitTweet)  #get most recent tweets
                    if len(search_results) > 0:
                        self.process_search_results(search_results)
        except Exception as e:
            print 'Error in twitter searching: %s' % e

    def process_search_results(self, search_results):
        """
        This records the search results in the couchdb and redis databases
        @param search_results Dictionary from twitter search with tweets stored in search_results['statuses']
        @type search_results Dictionary
        """
        statuses = search_results['statuses']  # This is the list returned which contains all the tweets
        self.tweets = []
        if len(statuses) > 0:
            stored = 0
            for tweet in statuses:
                try:
                    tweetid = tweet['id_str']
                    # Set the id field to id_str to ensure uniqueness
                    tweet['_id'] = tweetid
                    #save in couch
                    try:
                        self.db.save(tweet)
                        #If it saved in couch, save in redis. If it was a duplicate, it should throw exception
                        try:
                            self.redis_service.save_tweet_id(tweetid)
                            #If it saved in both couch and redis, save to graph
                            try:
                                ##This is the graph builder that has been disabled
                                ##self.build_from_single_tweet(tweet)
                                stored += 1
                            except Exception as e:
                                print 'Error saving tweetid %s to graph: %s' % (tweetid, e)
                        except Exception as e:
                            print 'Error storing tweetid %s in redis: %s ' % (tweetid, e)
                    except Exception as e:
                        pass
                    #print 'Error storing tweetid: %s in couchdb: %s' % (tweetid, e)
                except Exception as e:
                    print 'Error with loop on tweet: %s' % e


"""
def newsearch:
self.search_results = self.twitter_conn.search.tweets(q=self.word_map_table_creation_query, count=100)
"""
