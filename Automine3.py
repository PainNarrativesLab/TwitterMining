"""
Mines twitter for terms. Prints to log file rather than screen
"""
"""
This module runs from the python terminal. (Not from ipython)
This automatically mines twitter for the search terms
Periodically rests to avoid rate limits
"""
import sys

import TwitterSearcher2 as TS
from CouchDBTools import CompileTweets


# removed #TN on 1June
#search_terms = ['#Spoonie', '#CRPS', '#Migraine',
#'#RSD', '#Fibro', '#Fibromyalgia',
#'#Vulvodynia', '#ChronicPain', '#pain', '#endometriosis', '#neuropathy', '#arthritis', '#neuralgia']

search_terms = ['Spoonie',
                'CRPS',
                'Migraine',
                'RSD',
                'Fibro',
                'Fibromyalgia',
                'Vulvodynia',
                'ChronicPain',
                'pain',
                'endometriosis',
                'neuropathy',
                'arthritis',
                'neuralgia']


limit = 10000
LOGFILE = '/Users/adam/Desktop/twitter_miner_log.txt'
REST = 800  #Interval to rest between runs
credentials = '/Users/adam/Dropbox/PainNarrativesLab/private_credentials/twittercredentials.xml'


class LogWriter:
    def write(self, stuff):
        f = open(LOGFILE, 'a')
        f.write(stuff)
        f.close()


def stdin2file(func, file_like):
    def innerfunc(*args, **kwargs):
        old = sys.stdout
        sys.stdout = file_like
        try:
            return func(*args, **kwargs)
        finally:
            sys.stdout = old

    return innerfunc


def getNewerTweets():
    """
    Call this to get the most recent tweets for the search list
    """
    recent = 'True'
    ts = TS.Search(credentials)
    ts.run(search_terms, limit, recent, REST)


def getOlderTweets():
    """
    Call this to get tweets older than those already stored
    """
    recent = 'False'
    ts = TS.Search()
    ts.run(search_terms, limit, recent, REST)


def getNewHashtag(tag):
    """
    This does getOLderTweets but does all the runs for the new hashtag
    """
    #i=0
    #while i < limit:
    #        print 'Getting older tweets for %s' % tag
    #        print datetime.now()
    #        print 'Run number: %d' %i
    #        for j in range(5):
    #                ts = TS.Search()
    #                ts.execute(tag, 'False')
    #        print 'resting'
    #        print datetime.now()
    #        sleep(600)
    #        i+=1


getNewerTweets = stdin2file(getNewerTweets, LogWriter())

getNewerTweets()

#getOlderTweets()
#getNewHashtag('#neuropathy')
