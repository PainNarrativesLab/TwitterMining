"""
This creates a sqlite database with the structure of the mysql database
for unit testing database interaction

"""
__author__ = 'ars62917'

import sqlite3


class TestingDao(object):
    def __init__(self):
        self.conn = sqlite3.connect(':memory:');
        self.cursor = self.conn.cursor()

    def make_tables(self):
        self._make_hashtags_table()
        self._make_tweets_table()
        self._make_tweetsxtags_table()
        self._make_users_table()

    def close_connection(self):
        self.conn.close()

    def _make_hashtags_table(self):
        self.cursor.execute("""CREATE TABLE hashtags (
        tagID INTEGER PRIMARY KEY AUTOINCREMENT,
        hashtag TEXT unique)""")
        self.conn.commit()

    def _make_tweets_table(self):
        self.cursor.execute("""
        CREATE TABLE `tweets` (
        `tweetID` INTEGER PRIMARY KEY,
        `userID` TEXT,
        `tweetText` TEXT,
        `favorite_count` TEXT,
        `source` TEXT,
        `retweeted` TEXT,
        `in_reply_to_screen_name` TEXT,
        `retweet_count` TEXT,
        `favorited` TEXT,
        `lang` TEXT,
        `created_at` TEXT,
        `updated` TEXT,
        `profile_background_tile` TEXT)
        """)
        self.conn.commit()

    def _make_users_table(self):
        self.cursor.execute("""
        CREATE TABLE `users` (
        `userID` INTEGER PRIMARY KEY,
        `lang` TEXT,
        `utc_offset` TEXT,
        `verified` TEXT,
        `description` TEXT,
        `friends_count` TEXT,
        `url` TEXT,
        `time_zone` TEXT,
        `created_at` TEXT,
        `name` TEXT,
        `entities` TEXT,
        `followers_count` TEXT,
        `screen_name` TEXT,
        `id_str` TEXT,
        `favourites_count` TEXT,
        `statuses_count` TEXT,
        `id` TEXT,
        `location` TEXT)
        """)
        self.conn.commit()

    def _make_tweetsxtags_table(self):
        self.cursor.execute("""CREATE TABLE `tweetsXtags` (
        `tweetID`TEXT,
        `tagID` TEXT)
        """)
        self.conn.commit()

    def executeQuery(self):
        """
        Prepares and executes the query stored in self.query with the variables in self.val
        Usually used for insert, update, and other functions which don't require a return
        """
        try:
            # self.checkValName()
            self.cursor.execute(self.query, self.val)
            self.cnt = self.conn.total_changes
        except Exception as e:
            print "Query failed: %s" % e

    def returnOne(self):
        """
        Executes the query stored in self.query with the vals in self.val.
        Returns the first row in an array called self.results
        """
        try:
            # self.checkValName()
            self.cursor.execute(self.query % self.val)
            self.results = self.conn.fetchone()
        except Exception as e:
            print "Query failed: %s " % e

    # raise

    def returnAll(self):
        """
        Executes the query stored in self.query with the vals in self.val.
        Return the results in an array called self.results
        """
        try:
            # self.checkValName()
            self.conn.execute(self.query, self.val)
            self.results = self.cursor.fetchall()
        except Exception as e:
            print "Query failed: %s " % e
            raise

    def returnInsertID(self):
        """
        Returns the id of the last insert statement. Also sets self.insertedid with this value
        """
        try:
            return self.cursor.lastrowid
        except Exception as e:
            print "Error getting insert id %s " % e

# class MyTestCase(unittest.TestCase):
#     def setUp(self):
#         self.dao = TestingDao()
#         self.dao.make_tables()
#
#     def test_something(self):
#         self.dao.query = """INSERT INTO hashtags (hashtag) VALUES ('testtag')"""
#         self.dao.val = []
#         self.dao.executeQuery()
#         insertid = self.dao.returnInsertID();
#         #self.dao.query = """
#         #self.dao.returnAll()
#         print insertid
#         # self.assertTrue(insertid, 0)


if __name__ == '__main__':
    pass
    # unittest.main()
