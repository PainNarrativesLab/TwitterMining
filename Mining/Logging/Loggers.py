from datetime import datetime
from logbook import Logger
import os


class LogWriter(object):
    """
    Parent class for loggers which write to a textfile
    """

    def __init__(self):
        self.initialize_logger()

    def initialize_logger(self):
        try:
            if self.logger is not None:
                pass
        except:
            self.logger = Logger()
            # self.logger = FileHandler(self.log_file)
            # self.logger.push_application() #Pushes handler onto stack of log handlers

    def set_log_file(self, file_to_write):
        self.logfile = file_to_write

    def write(self, stuff):
        f = open(self.logfile, 'a')
        f.write(stuff)
        f.close()


class SearchLogger(LogWriter):
    """
    Handles logging and printing information about search
    """

    def __init__(self, log_file='twitter_miner_log.txt'):
        self.log = ''
        LogWriter.__init__(self)
        self.log_file = log_file
        # self.UPATH = os.getenv("HOME")
        # self.log_file = '%s/Desktop/%s' % self.UPATH, log_file
        # self.log_file = "application_search.log"
        self.set_log_file(self.log_file)

    def write_to_file(self):
        self.write(self.log)
        self.log = ''

    def run_start(self, run_number):
        self.log += '\n --------------------------------- %s --------------------------- ' % datetime.now()
        self.log += "\n Run number: %d " % run_number
        self.write_to_file()
        print self.log

    def limit_tweet(self, limitTweet, recent):
        if recent is True:
            self.log += "\n Getting newer tweets "
        else:
            self.log += "\n Getting older tweets "
        self.log += "\n starting from tweet %s" % limitTweet
        self.write_to_file()

    def rest_start(self):
        self.log += '\n start resting: %s ' % datetime.now()
        self.write_to_file()

    def search_term(self, tag):
        self.log += '\n Searching for %s ' % tag
        self.write_to_file()
        # self.write(self.log)
        # print self.log

    def number_of_results(self, tag, num_results):
        self.log += '\n    Retrieved %s tweets for search on %s' % (num_results, tag)
        self.write_to_file()
        # print self.log

    def record_saver_action(self, savername, num_tweets):
        """
        This will be called inside the observer to log a saver class action
        Args:
            savername: String name of the saver (mysql, redis, couchdb)
            num_tweets: Integer number of tweets saved
        """
        self.log += '\n         Called saver for %s to save %s tweets' % (savername, num_tweets)
        self.write_to_file()

