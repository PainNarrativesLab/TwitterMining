"""
This holds the exception handling and logging classes
"""

import logbook

from logbook import FileHandler, Logger

class LoggableError(Exception):
    """
    Parent class for customized exception classes which provides interface to the logging functions
    
    Attributes:
        log_file: The file in which to keep logs
        logger: Instance of logbook.Handler which handles logging
    """
    def __init__(self):
        self.log_file = "application.log"
        self.initialize_logger()
        
    def initialize_logger(self):
        try:
            if self.logger != None:
                pass
        except:
            self.logger = Logger()
            #self.logger = FileHandler(self.log_file)
            #self.logger.push_application() #Pushes handler onto stack of log handlers

    
    def log_error(self, error_message):
        self.logger.error(error_message)
    
    def log_warning(self, warning_message):
        self.logger.warn(warning_message)
        

class TweetError(LoggableError):
    def __init__(self, tweetID):
        """
        Initializes log handler and creates message. Does not log. That should be handled by child classes
        """
        LoggableError.__init__(self)
        self.initialize_logger()
        self.tweetID = tweetID
        self.error_message = "%s went bad on tweetID %s" % (self.kind, self.tweetID)
    
    def __repr__(self):
        return self.error_message

class TweetServiceError(TweetError):
    def __init__(self, tweetID):
        self.kind = 'TweetService'
        TweetError.__init__(self, tweetID)
        self.log_error(self.error_message)

class HashtagServiceError(TweetError):
    def __init__(self, tweetID):
        self.kind = 'HashtagService'
        TweetError.__init__(self, tweetID)
        self.log_error(self.error_message)

class UserServiceError(TweetError):
    def __init__(self, tweetID):
        self.kind = 'UserService'
        TweetError.__init__(self, tweetID)
        self.log_error(self.error_message)
        

class SaverError(LoggableError):
    """
    Error in a class which saves to some data storage
    
    Attributes:
        kind: String describing the kind of error or location of the error (e.g., TweetSaverService.CouchSaver.save)
        tweet_object: The problematic tweet object (instance of TwitterDataProcessor.Tweet)
    """
    def __init__(self, kind, tweet_object):
        self.kind = kind
        self._set_tweetID(tweet_object)
        self.error_message = "Error in %s with saving tweetID %s" % (self.kind, self.tweetID)
        LoggableError.__init__(self)
        self.log_error(self.error_message)
    
    def _set_tweetID(self, tweet_object):
        """
        Extracts the tweet id, if present, from the problematic object
        """
        if 'tweetID' in tweet_object:
            self.tweetID = tweetID
        else:
            self.tweetID = 'unspecified tweet id'

    def __repr__(self):
        return "Error with saving tweetID %s" % (self.tweetID)

class ObserverError(LoggableError):
    """
    Error class for problems with observer functions
    
    Attributes:
        problem_observer: The observer class causing the error
    """
    def __init__(self, observer):
        LoggableError.__init__(self)
        self.problem_observer = observer
        self.error_message = "Error with observer: %s" % (self.problem_observer.__toString())
    
    def __repr__(self):
        return self.error_message


#if __name__ == '__main__':
#    with log_handler.applicationbound():
#        main()