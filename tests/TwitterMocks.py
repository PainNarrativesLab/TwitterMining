
def login():
    return TwitterMock()

class search:
    def __init__(self):
        pass
    
    def tweets(self, q, count, since_id=None, max_id=None):
        result = {'query' : q, 'count' : count, 'since_id' : since_id, 'max_id' : max_id}
        print result
        return result

class TwitterMock:
    def __init__(self):
        self.response = 'defaultResponse'
        self.tweets = []
        self.search = search()
        tweets = self.tweets
        
    def set_response(self, response):
        self.response = response
    
    