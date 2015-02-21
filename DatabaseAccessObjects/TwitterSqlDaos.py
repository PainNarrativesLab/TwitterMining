from DatabaseAccessObjects import MySQLDAO


class TwitterSQLDAO(MySQLDAO.BaseDAO):
    """
    Base mysql database abstraction object for twitter mysql database.
    This should be called and loaded into the service objects via their set_dao() method
    """

    def __init__(self, credentials, **kwargs):
        """
        Arguments:
            credentials: SqlCredentials.Credentials
            kwargs: DEPRECATED includes test and local which remain to ensure compatibility with legacy code
        """
        MySQLDAO.BaseDAO.__init__(self)
        self.connect(credentials)


if __name__ == '__main__':
    pass