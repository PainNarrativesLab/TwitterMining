__author__ = 'adam'

from Mining.AutomaticMiner.ObserverAndSubscribers import ISearchObserver


class ISearchObserverMock(ISearchObserver):
    def __init__(self):
        ISearchObserver.__init__(self)
        self.tweets = []
        self.dbsavers = []
        self.caller = ''
        self.save_pending_called = False
        self.update_called = False
        self.dummytweet = {'tweet': True, 'dummy': True}

    def _add_to_pending_tweets(self, tweets):
        self.tweets.append(tweets)

    def subscribe_db_saver(self, dbobject):
        self.dbsavers.append(dbobject)

    def save_pending_tweets(self):
        self.save_pending_called = True

    def update(self, subject):
        self.update_called = True
        self.caller = subject

    def _save_tweet(self, tweet):
        self.tweets.append(tweet)

    def _get_next_pending_tweet(self):
        return self.dummytweet

if __name__ == '__main__':
    pass