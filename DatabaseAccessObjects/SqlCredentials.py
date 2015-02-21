__author__ = 'adam'
"""
Credentials for mysql database access
"""

from sqlalchemy import create_engine


class Credentials(object):
    """
    This is the parent class for the various credential classes which hold the login credentials for the mysql databases

    Attributes:
        db_host: String location of the host with the database
        db_user: String username for accessing the database
        db_name: String name of the database schema
        db_password: String password for accessing the database
        db_port: String port at which database is located
    """

    def __init__(self):
        self.db_host = "mysqlent.csun.edu"
        self.db_user = ''
        self.db_name = ''
        self.db_password = ''
        self.db_port = '42424'

    def host(self):
        """
        Returns:
            String location of host
        """
        return self.db_host

    def database(self):
        """
        Returns:
            String name of the database schema
        """
        return self.db_name

    def password(self):
        """
        Returns:
            String password for schema
        """
        return self.db_password

    def username(self):
        """
        Returns:
            String username for access
        """
        return self.db_user


    def port(self):
        """
        Returns:
            String identifying port to connect with
        """
        return self.db_port

    def sql_alchemy_engine(self):
        """
        Creates a mysql alchemy engine for connecting to the db with the format:
         dialect+driver://username:password@host:port/database
        """
        engine_string = "mysql://%s:%s@%s:%s/%s" % (self.db_user, self.db_password, self.db_host, self.db_port, self.db_name)
        return create_engine(engine_string)


class TestingCredentials(Credentials):
    """
    These are dummy credentials for testing
    """
    def __init__(self):
        Credentials.__init__(self)
        self.username = 'testusername'
        self.db_name = 'testdbname'
        self.password = 'testpassword'
        self.port = 'testport'
