from datetime import datetime
from logbook import Logger


class LogWriter(object):
    """
    Parent class for loggers which write to a textfile
    """

    def __init__(self):
        self.log_file = "application_search.log"
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

    def __init__(self):
        self.log = ''
        LogWriter.__init__(self)

    def run_start(self, run_number):
        self.log += '--------------------------------- %s --------------------------- \n' % datetime.now()
        self.log += "Run number: %d \n" % run_number
        print self.log

    def limit_tweet(self, limitTweet, recent):
        if recent is True:
            self.log += "Getting newer tweets \n"
        else:
            self.log += "Getting older tweets \n"
        self.log += "starting from tweet %s" % limitTweet

    def rest_start(self):
        self.log += 'start resting: %s \n' % datetime.now()

    def search_term(self, tag):
        self.log += 'Searching for %s \n' % tag
        print self.log

    def number_of_results(self, tag, num_results):
        self.log += '    Retrieved %s tweets for search on %s' % (num_results, tag)
        print self.log

    def write_to_file(self):
        self.write(self.log)