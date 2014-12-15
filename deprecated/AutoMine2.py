"""
This module runs from the python terminal. (Not from ipython)
This automatically mines twitter for the search terms
Periodically rests to avoid rate limits
"""
import TwitterSearcher2 as TS

from TwitterServiceClasses import CompileTweets

#removed #TN on 1June
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

def getNewerTweets():
	"""
	Call this to get the most recent tweets for the search list
	"""
	recent = 'True'
	ts = TS.Search()
	ts.run(search_terms, limit, recent)


def getOlderTweets():
	"""
	Call this to get tweets older than those already stored
	"""
	recent = 'False'
	ts = TS.Search()
	ts.run(search_terms, limit, recent)

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

getNewerTweets()
#getOlderTweets()
#getNewHashtag('#neuropathy')