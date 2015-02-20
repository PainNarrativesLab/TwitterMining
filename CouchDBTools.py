from datetime import datetime
from couchdb.design import ViewDefinition
from DatabaseAccessObjects.CouchDBDAOs import CouchDAO

__author__ = 'ars62917'


class CouchService(object):
    """
    Handles operations upon the couchdb dataabase specific to tweet stuff


    """
    def __init__(self):
        self.min_id_view = None
        self.max_id_view = None

    def set_dataservice(self, couchdao):
        """
        Sets the connection to the database to be used
        Args:
            couchdao: CouchDBDAOs.CouchDao object
        """
        self.dao = couchdao

    def get_newest_id(self):
        try:
            v = self.dao.get_view('indexpy/maxid')
            # unnecessary right?
            if len(v) > 1:
                maxids = []
                for i in v:
                    maxids.append(i)
            else:
                for i in v:
                    self.max_id = i.value
            self.newest = self.max_id
        except Exception as e:
            print "No newest loaded %s" % e

    def get_oldest_id(self):
        try:
            v = self.dao.get_view('indexpy/minid')
            for i in v:
                self.min_id = i.value
            self.oldest = self.min_id
        except Exception as e:
            print "No oldest loaded %s" % e

    def get_tweetids(self):
        """
        Gets the tweetids (i.e., id_str) from each record

        Returns:
            List of tweet ids
        """
        try:
            v = self.dao.get_view('indexpy/tweetids')
            self.tweetids = []
            for i in v:
                self.tweetids.append(i.value)
            return self.tweetids
        except Exception as e:
            print "Error loading ids %s" % e

    def get_tweet_texts(self):
        """
        Gets texts of tweets from couchdb

        Returns:
            List of texts from tweets
        """
        query = self.dao.query("""function(doc){emit (null, doc.text);}""")
        self.text = []
        for i in query:
            self.text.append(i.value)
        return self.text

    def make_view(self, name, javascript_function):
        try:
            mapper = """function(doc){emit(doc.id_str, doc.id_str);}"""
            vw = ViewDefinition('index', name, mapper)
            vw.sync(self.db)
        except Exception as e:
            print "Error making maxid view %s" % e

    def make_tweet_views(self):
        """
        DEPRECATED do not call
            old code for reference
            mapper = "function(doc){emit(doc.id_str, doc.id_str);}"
            vw = ViewDefinition('index', 'max_min_ids', mapper, '_stats')
            vw.sync(self.db)
        """
        raise AttributeError

    def get_max_min_ids(self):
        """
        DEPRECATED Should use get_oldest_id and get_newest_id instead"
        Old code for reference:
        # Get max id
            #v = self.db.view('index/max_min_ids')
            #for i in v:
            #       self.max_id = i.value['max']
            #       self.min_id = i.value['min']
            #self.oldest = self.min_id
            #self.newest = self.max_id
        """
        raise AttributeError('Deprecated method called');


class CompileTweets:
    """
    Service class for compiling various searchdbs into one database with str_id as unique keys
    """

    @staticmethod
    def run(resultdbs):
        compiled_dao = CouchDAO()
        compiled_dao.connect('compiled')
        compiled = CouchService()
        compiled.set_dataservice(compiled_dao)
        errors = []
        number_compiled = 0

        for db in resultdbs:
            db_dao = CouchDAO()
            db_dao.connect(db)
            db_service = CouchService()
            db_service.set_dataservice(db_dao)
            # texts = []
            print datetime.now(), "Compiling: %s" % (db)
            for row in db_service.dao.get_view('indexpy/get_tweets'):
                #                       for row in cdb.db.query("""function(doc){emit (null, doc);}"""):
                #       texts.append(row.value)
                try:
                    # for t in row.value:
                    # for t in texts:
                    # Check whether already exists
                    tweetid = row.value['id_str']
                    try:
                        existing = compiled.db[tweetid]
                    except:
                        # if except then tweet isn't in compiled
                        row.value['_id'] = tweetid
                        compiled.dao.save(row.value)
                        number_compiled += 1
                except:
                    errors.append(row.value)
        print "%i tweets processed with %i errors" % (number_compiled, len(errors))

#
# class CouchSaver:
#     """
#     Service class for one-off saving document to couchdb
#     """
#
#     @staticmethod
#     def save(database_name, document):
#         try:
#             # dao = CouchDAO.__init__(self)
#             # self.connect(database_name)
#             dbc = CouchService(database_name)
#             a = dbc.db.save(document)
#             # print a
#             #print 'jap'
#         except:
#             print e
