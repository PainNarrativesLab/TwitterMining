"""
This condenses the tags found in the tweets via importing them to reddis
This is to be ran from idle or terminal (much faster than running from ipython)

"""
import TwitterServiceClasses as TSC
from TwitterDataProcessors import TagsFromSearch
import pickle
try:
    RS = TSC.RedisService()

    #Databases containing tweets
    resultdbs = ['search-spoonie', 'search-crps', 'search-migraine', 'search-tn', 'search-rsd', 'search-fibro', 'search-fibromyalgia', 'search-vulvodynia', 'search-chronicpain']
    for db in resultdbs:
        RS.hashtags_from_search_to_redis(db)

    #Retrieve all tags
    RS = TSC.RedisService()
    RS.get_all_tags()
    RS.remove_redis_format_from_stored_tags()
    cr = len(RS.clean_results)
    print "%d tags cleaned and returned" % cr
    TFS = TagsFromSearch()
    pairs, alltags = TFS.getPairs(RS.clean_results)
    print "%d pairs identified" % len(pairs)
    print "%d total tags" % len(alltags)
except Exception as e:
    print e

finally:
    #save pairs
    with open('pairs', 'w') as f:
        pickle.dump(pairs, f)
    #save all
    with open('alltags', 'w') as f:
        pickle.dump(alltags, f) 