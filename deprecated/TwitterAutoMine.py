"""
This module runs from the python terminal. (Not from ipython)
This automatically mines twitter for the search terms
Periodically rests to avoid rate limits
"""
from time import sleep
from datetime import datetime

import TwitterSearcher as TS

from TwitterServiceClasses import CompileTweets


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

#List of search databases to compile from
#resultdbs = ['n-search-spoonie',
#			     'n-search-crps',
#			     'n-search-migraine',
#			     'n-search-pain',
#			     'n-search-rsd',
#			     'n-search-fibro',
#			     'n-search-fibromyalgia',
#			     'n-search-vulvodynia',
#			     'n-search-chronicpain',
#			     'n-search-endometriosis',
#			     'n-search-neuropathy',
#			     'n-search-arthritis', 'n-search-neuralgia']

limit = 1000


def getNewerTweets():
    """
    Call this to get the most recent tweets for the search list
    """
    i = 0
    while i <= limit:
        print "++++++++++"
        print 'Compiling', datetime.now()
        dbs = []
        for term in search_terms:
            term = term.lower()
            resultdb = 'n-search-%s' % term
            dbs.append(resultdb)

        CompileTweets.run(dbs)
        #CompileTweets.run(resultdbs)
        #print datetime.now()
        print '------------------------------------------------------------------'

        print 'Getting newer tweets....'
        print datetime.now()
        print "Run number: %d" % i
        idx = 0
        for s in search_terms:
            hashtag = '#%s' % s
            ts = TS.Search()
            ts.execute(hashtag, 'True')
            if idx % 2 == 0:
                print 'resting'
                print datetime.now()
                sleep(600)
            idx += 1
        i += 1


def getOlderTweets():
    """
    Call this to get tweets older than those already stored
    """
    i = 0
    print 'Getting older tweets....'
    while i <= limit:
        print 'Go!'
        print datetime.now()
        print "Run number: %d" % i
        for s in search_terms:
            ts = TS.Search()
            ts.execute(s, 'False')
            print 'resting'
            print datetime.now()
            sleep(600)
        i += 1


def getNewHashtag(tag):
    """
    This does getOLderTweets but does all the runs for the new hashtag
    """
    i = 0
    while i < limit:
        print 'Getting older tweets for %s' % tag
        print datetime.now()
        print 'Run number: %d' % i
        for j in range(5):
            ts = TS.Search()
            ts.execute(tag, 'False')
        print 'resting'
        print datetime.now()
        sleep(600)
        i += 1


#getOlderTweets()
getNewerTweets()
#getNewHashtag('#neuropathy')




