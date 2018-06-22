# The working tweet searcher
import sys
from datetime import date

import twitter
import couchdb
from couchdb.design import ViewDefinition
import networkx as nx

from TwitterUtilities import makeTwitterRequest
from TwitterLogin import login
from TwitterServiceClasses import CouchService
from TwitterServiceClasses import RedisService
from TwitterDataProcessors import Extractors


class GraphBuilder:
    """
    This will add the tweets to a stored graph to save time in analyzing graphs later
    """

    def __init__(self):
        """
        @param tweetlist The list containing all the tweets
        """
        # self.graphFile = 'tweet_hashtags_graph_MASTER.gexf'
        self.tweet_tuples = []
        self.errors = []
        #self.tweetlist = tweetlist
        ## @todo This won't work until something connects tweetlist to tweetObject

    def loadGraph(self):
        today = date.isoformat(date.today())
        self.graphFile = 'tweet_hashtags_graph_%s.gexf' % today
        try:
            graph = nx.read_gexf(self.graphFile)
            return graph
        except:
            g = nx.Graph()
            try:
                nx.write_gexf(g, self.graphFile)
                graph = nx.read_gexf(self.graphFile)
                return graph
            except:
                print 'Something is very wrong with the graphfile retrieval'

    def builder(self, tweetlist):
        try:
            # load graph from file
            # graph = nx.read_gexf(self.graphFile)
            graph = self.loadGraph()
            print datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
            print 'Start graph info', nx.info(graph)
        except Exception as e:
            print 'Error loading graph from %s: %s' % (graphFile, e)
            # Prevent further execution
            sys.exit()
            #Add to graph
        try:
            for tweet in tweetlist:
                tweet_tuples = []
                entities = Extractors.getEntities(tweet)
                if len(entities['hashtags']) >= 1:
                    list_of_hashtags = entities['hashtags']
                    for tag in list_of_hashtags:
                        tag_cleaned = str(tag['text'])
                        tag_cleaned = tag_cleaned.lower()
                        tweetid = tweet['id_str']
                        tweet_tuple = (tweetid, tag_cleaned)
                        tweet_tuples.append(tweet_tuple)
                    try:
                        graph.add_edges_from(tweet_tuples)
                    except Exception as e:
                        print 'Error adding edges to graph %s', e
        except Exception as e:
            print 'Error in building graph %s' % e
        finally:
            nx.write_gexf(graph, self.graphFile)
            print 'Saved graph info : ', nx.info(graph)  # for tweet in tweetObject:


class Search(CouchService, GraphBuilder):
    """
    Does the searching
    """

    def __init__(self):
        self.twitter_conn = login()
        self.redis_service = RedisService()

    def test(self):
        db_name = 'compiled'
        # connect
        try:
            CouchService.__init__(self, db_name)
        except Exception as e:
            print 'Problem connecting to couchdb database: %s', e

        #Display oldest and newest ids from db
        try:
            self.get_oldest_id()
            print 'Oldest id is %s', self.oldest
            self.get_newest_id()
            print 'Newest id is %s', self.newest
        except Exception as e:
            print 'Problem getting oldest/ newest id from %s: %s', (db_name, e)

    def quickrun(self, query_string, recent='True'):
        """
        Performs the search.
        @param query_string The word_map_table_creation_query to send to twitter
        @type query_string string
        @param recent 'True' search for tweets newer than most recent record; 'False' search for tweets older than oldest record
        @type recent string
        @todo Revise so that the only checks the starting tweet id once per group of word_map_table_creation_query terms
        """
        # Query
        self.query = query_string
        self.MAX_PAGES = 10
        db_name = 'compiled'
        #connect
        CouchService.__init__(self, db_name)
        self.tweets = []
        """
        @todo Rewrite the create view methods in couchservice. Then can add something here to create new views if the views don't exist
        """
        try:
            ##Check for where previous searches left off and run
            for _ in range(self.MAX_PAGES - 1):  # Get more pages
                try:
                    if recent == 'False':
                        print 'doing old'
                        self.get_oldest_id()
                        self.search_results = self.twitter_conn.search.tweets(q=self.query, count=100,
                                                                              max_id=self.oldest)  #tweets before ealiest record
                    else:
                        print 'doing new'
                        #self.get_newest_id()
                        self.redis_service.get_max_id()
                        print 'Newest stored tweet %s' % self.redis_service.maxid
                        self.search_results = self.twitter_conn.search.tweets(q=self.query, count=100,
                                                                              since_id=self.redis_service.maxid)  #get most recent tweets
                        #self.search_results = self.twitter_conn.search.tweets(q=self.word_map_table_creation_query, count=100, since_id=self.newest)  #get most recent tweets
                except Exception as e:  # If there are no results in the db already
                    print 'none in db %s' % e
                    self.search_results = self.twitter_conn.search.tweets(q=self.query, count=100)
                    #check whether the tweet has already been saved
                ignored = 0  # counter for how many ignored
            #for status in self.search_results['statuses']:
            try:
                statuses = self.search_results['statuses']  # This is the list returned which contains all the tweets

                newtweets = []
                for tweet in statuses:
                    present = self.redis_service.lookup_tweet_id(tweet['id_str'])
                    if present is True:  # Already have the tweet
                        #print 'already have: %s' % str(tweet['id_str'])
                        ignored += 1
                    elif present is False:
                        newtweets.append(tweet)
                        self.redis_service.save_tweet_id_to_master_list(tweet['id_str'])
                    if len(newtweets) > 0:
                        self.tweets += newtweets
            except Exception as e:
                print 'problem looking up tweet'
                print 'error %s' % e
                #print 'Fetched %i tweets so far' % (len(self.tweets),)
                #print 'Ignored %i tweets as duplicates' % ignored
        except Exception as e:
            print 'error %s' % e

        finally:
            #If the word_map_table_creation_query loop finishes or if it hits an error, record the results in couchdb
            for t in self.tweets:
                try:
                    t['_id'] = t['id_str']
                    self.db.save(t)
                    self.redis_service.save_tweet_id(t['id_str'])
                except:
                    pass
                    #print 'Did not save %s' % str(t['id_str'])
                    #self.db.update(self.tweets, all_or_nothing=True)
        print '%s: Done. Stored data to %s' % (self.query, self.db,)
        print '%i new tweets stored' % (len(self.tweets, ))
        try:
            #pass
            GraphBuilder.__init__(self)
            self.builder(self.tweets)
        except Exception as e:
            print 'Your builder function sucks %s', e

    def execute(self, query_string, recent='True'):
        """
        Performs the search.
        @param query_string The word_map_table_creation_query to send to twitter
        @type query_string string
        @param recent 'True' search for tweets newer than most recent record; 'False' search for tweets older than oldest record
        @type recent string
        """
        # Query
        self.query = query_string
        self.MAX_PAGES = 10
        db_name = 'n-search-%s' % (self.query.lower().replace('#', '').replace('@', ''), )
        #connect
        CouchService.__init__(self, db_name)
        self.tweets = []
        """
        @todo Rewrite the create view methods in couchservice. Then can add something here to create new views if the views don't exist
        """
        try:
            ##Check for where previous searches left off and run
            for _ in range(self.MAX_PAGES - 1):  # Get more pages
                try:
                    if recent == 'False':
                        self.get_oldest_id()
                        self.search_results = self.twitter_conn.search.tweets(q=self.query, count=100,
                                                                              max_id=self.oldest)  #tweets before ealiest record
                    else:
                        self.get_newest_id()
                        self.search_results = self.twitter_conn.search.tweets(q=self.query, count=100,
                                                                              since_id=self.newest)  #get most recent tweets
                except:  # If there are no results in the db already
                    self.search_results = self.twitter_conn.search.tweets(q=self.query, count=100)
                    #check whether the tweet has already been saved
                ignored = 0  # counter for how many ignored
            #for status in self.search_results['statuses']:
            try:
                statuses = self.search_results['statuses']  # This is the list returned which contains all the tweets

                newtweets = []
                for tweet in statuses:
                    present = self.redis_service.lookup_tweet_id(tweet['id_str'])
                    if present is True:  # Already have the tweet
                        #print 'already have: %s' % str(tweet['id_str'])
                        ignored += 1
                    elif present is False:
                        newtweets.append(tweet)
                        #self.save_tweet_id(tweet['id_str'])
                        #self.redis_service.save_tweet_id_to_master_list(tweet['id_str'])
                    if len(newtweets) > 0:
                        self.tweets += newtweets
            except Exception as e:
                print 'problem looking up tweet'
                print 'error %s' % e
                #print 'Fetched %i tweets so far' % (len(self.tweets),)
                #print 'Ignored %i tweets as duplicates' % ignored
        except Exception as e:
            print 'error %s' % e

        finally:
            #If the word_map_table_creation_query loop finishes or if it hits an error, record the results in couchdb
            for t in self.tweets:
                try:
                    t['_id'] = t['id_str']
                    self.db.save(t)
                    self.save_tweet_id(tweet['id_str'])

                except:
                    pass
                    #print 'Did not save %s' % str(t['id_str'])
                    #self.db.update(self.tweets, all_or_nothing=True)
        print '%s: Done. Stored data to %s' % (self.query, self.db,)
        print '%i new tweets stored' % (len(self.tweets, ))


