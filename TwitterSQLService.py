"""
Service classes for mysql database holding twitter stuff
"""
from DatabaseAccessObjects import TwitterSqlDaos as DAO


class SQLService(DAO.TwitterSQLDAO):
    def __init__(self, credentials, **kwargs):
        DAO.TwitterSQLDAO.__init__(self, credentials, **kwargs)


class QueryShell(DAO.TwitterSQLDAO):
    """
    This is just a shell to easily run queries on the database and get the results as a list of dictionaries

    @return Returns list of dictionaries
    """

    def __init__(self, credentials, **kwargs):
        DAO.TwitterSQLDAO.__init__(self, credentials, **kwargs)

    def runquery(self, query, val=[]):
        self.query = query
        self.val = val
        self.returnAll()
        return list(self.results)


if __name__ == '__main__':
    pass