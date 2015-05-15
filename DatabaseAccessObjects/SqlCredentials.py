__author__ = 'adam'
"""
Credentials for mysql database access
"""

from sqlalchemy import create_engine
import xml.etree.ElementTree as ET


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
        self.db_host = ""
        self.db_user = ''
        self.db_name = ''
        self.db_password = ''
        self.db_port = ''

    def load_credentials(self, credentials_file):
        """
        Imports the database connection credentials from xml file

        Args:
         credentials_file: Path and filename to the credentials file to use
        """
        credentials = ET.parse(credentials_file)
        self.db_host = credentials.find('db_host').text
        self.db_port = credentials.find('db_port').text
        if self.db_port is not None:
            self.db_port = int(self.db_port)
        self.db_user = credentials.find('db_user').text
        self.db_name = credentials.find('db_name').text
        self.db_password = credentials.find('db_password').text

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
        if self.db_port is not None:
            return self.db_port

    def sql_alchemy_engine(self):
        """
        Creates a mysql alchemy engine for connecting to the db with the format:
         dialect+driver://username:password@host:port/database
        """
        if self.db_port is not None:
            engine_string = "mysql://%s:%s@%s:%s/%s" % (self.db_user, self.db_password, self.db_host, self.db_port, self.db_name)
        else:
            engine_string = "mysql://%s:%s@%s/%s" % (self.db_user, self.db_password, self.db_host, self.db_name)
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
