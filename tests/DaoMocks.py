
class DaoMock:
    
    def __init__(self, test=False, local=True):
        self.query = ''
        self.val = ''
        self.runcount = 0
        self.test = test
        self.local = local
        self.response = None
        self.log = []
    
    def log_query(self, command):
        self.log.append({'run_num' : self.runcount, 'query' : self.query, 'val' : self.val, 'command' : command})
        self.runcount += 1
    
    def set_response(self, response):
        self.response = response
    
    def returnAll(self):
        self.log_query('returnAll')
        if(self.response != None):
            self.result = self.response
            self.results = self.response
        else:
            self.result = 'returnAll'
            self.results = 'returnAll'
        return self.results
    
    def executeQuery(self):
        self.log_query('executeQuery')
        if(self.response != None):
            self.result = self.response
            self.results = self.response
        else:
            self.result = 'executeQuery'
            self.results = 'executeQuery'
        return self.results
    
    def returnOne(self):
        self.log_query('returnOne')
        if(self.response != None):
            self.result = self.response
            self.results = self.response
        else:
            self.result = 'returnOne'
            self.results = 'returnOne'
        return self.results

class RedisDaoMock:
    
    def __init__(self):
        self.response = 'defaultResponse'
    
    def set_response(self, response):
        self.response = response
    
    def get_oldest_id(self):
        return self.response
    
    def get_max_id(self):
        self.maxid = self.response
        return self.response
    
    def save_tweet_id(self, tweetid):
        pass

class CouchDaoMock:
    def __init__(self):
        self.response = 'defaultResponse'
    
    def set_response(self, response):
        self.response = response