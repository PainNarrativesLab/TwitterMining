#import DatabaseAccessObjects.RedisDAOs
#import DatabaseAccessObjects.CouchDBDAOs
#
#tweets = 0
#
#cdb = DatabaseAccessObjects.CouchDBDAOs.CouchDAO()
#cdb.connect('compiled')
#rdao = DatabaseAccessObjects.RedisDAOs.RedisDAO()
#for tid in cdb.db:
#    rdao.db.sadd('alltweets', tid)
#    tweets += 1
#print "%s tweets added" % tweets
#

import pycurl
from StringIO import StringIO
import json
import Mining.DatabaseAccessObjects.RedisDAOs
class CouchIdGetter( Mining.DatabaseAccessObjects.RedisDAOs.RedisDAO ):
    """
    This pulls all doc ids from couch to find ones missing from tweetids in redis
    Attributes:
        redisdao: RedisDao object
        couchdao: CouchDBDao object
        starting_tweet: The minimum value stored in mysql
        ending_tweet: The maximum value stored in mysql
        increment: The amount to increase the search ids
        recorded: Counter for number of tweets recorded
    """
    def __init__(self, dbname='n-search-crps', db=0, start=4021982852191600065):
        self.storage_set_name = 'couchdbtweetIDs'
        if db is not 0:
            Mining.DatabaseAccessObjects.RedisDAOs.RedisDAO.__init__( self, db )
        else:
            Mining.DatabaseAccessObjects.RedisDAOs.RedisDAO.__init__( self )
        self.minerip = 'localhost:5984'
        #self.minerip = '169.254.203.246:5984'
        self.dbname = dbname
        self.starting_tweet = start
        self.bottom_limit = 200000000000000000
        self.upper_limit = 576097546914807808
        self.increment = 10000000000000
        self.minid = None
        self.maxid = None
        self.recorded = 0
        
    def check_for_less_than_starting(self):
        """
        Checks to make sure no tweets in db with ids before starting value
        """
        try:
            self.maxid = self.starting_tweet
            self.minid = self.maxid - self.increment
            #print self.minid, self.maxid
            while True:
                result = self._search(self.minid, self.maxid)
 #               print self.recorded, len(result), self.minid, self.maxid
                for row in result:
                    if row['id'] is not '_design/index':
                        self.db.sadd(self.storage_set_name, row['id'])
                        self.recorded += 1
 #                       print self.recorded
                self.maxid = self.minid
                self.minid -= self.increment
                if self.maxid < self.bottom_limit:
                    break
            
        except Exception as e:
            print "Error: %s" % e
        print "%s tweets recorded" % self.recorded
   
    
    def check_for_greater_than_starting(self):
        """
        Checks for values greater than starting
        """
        try:
            self.minid = self.starting_tweet
            self.maxid = self.minid + self.increment
            while True:
 #               print self.recorded, self.minid, self.maxid
                result = self._search(self.minid, self.maxid)
 #               print len(result)
                for row in result:
                    if row['id'] is not '_design/index':
                        self.db.sadd(self.storage_set_name, row['id'])
                        self.recorded += 1
                self.minid = self.maxid
                self.maxid += self.increment
                if self.minid > self.upper_limit:
                    break
        except Exception as e:
            print "Error: %s" % e
        print "%s tweets recorded" % self.recorded
            
    def _search(self, startid, stopid):
        """
        Returns:
            List of dicts with key 'id'
        startid = 4021982852191600065
        stopid = 400254646977298433
        """
        request = 'http://%s/%s/_all_docs?startkey="%s"&endkey="%s"' % (self.minerip, self.dbname, startid, stopid)
        buffer = StringIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL, request)
 #       c.setopt(pycurl.GETFIELDS, dt) 
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        body = json.loads(buffer.getvalue())
 #       print body
        return body['rows']

c = CouchIdGetter(dbname='compiled', start=576187049604096000)
#c.check_for_greater_than_starting()
c.check_for_less_than_starting()

##rdao = DatabaseAccessObjects.RedisDAOs.RedisDAO()
##
##def search(startid, stopid, minerip='localhost:5984', dbname='n-search-crps'):
##    buffer = StringIO()
####    request = 'http://%s/%s/_all_docs?startkey_docid=%s&endkey_docid=%s&descending=true' % (minerip, dbname, startid, stopid)
##    request = 'http://%s/%s/_all_docs?startkey="%s"&endkey="%s"' % (minerip, dbname, startid, stopid)   
##    c = pycurl.Curl()
##    c.setopt(pycurl.URL, request)
##    c.setopt(c.WRITEDATA, buffer)
##    c.perform()
##    c.close()
##    body = json.loads(buffer.getvalue())
##    print body
##    return body['rows']
##
##start = 399553052736098305
##while True: 
##    inc = 1000
##    stop = start + inc
##    result = search(start, stop)
##    print start, stop
##    for row in result:
##        print row['id']
##        rdao.db.sadd('couchdbtweetIDs', row['id'])
##    start = stop
##    if start is 400000000000000000:
##        break
