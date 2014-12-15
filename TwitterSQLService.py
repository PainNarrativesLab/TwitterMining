"""
Service classes for mysql database holding twitter stuff
"""
import TwitterSqlDaos as DAO

class SQLService(DAO.TwitterSQLDAO):
    def __init__(self, test=False, local=True):
        DAO.TwitterSQLDAO.__init__(self, test=test, local=local)


class QueryShell(DAO.TwitterSQLDAO):
	"""
	This is just a shell to easily run queries on the database and get the results as a list of dictionaries
	
	@return Returns list of dictionaries
	"""
	def __init__(self):
	    DAO.TwitterSQLDAO.__init__(self, test=False, local=True)
	
	def runquery(self, query, val=[]):
	    self.query = query
	    self.val = val
	    self.returnAll()
	    return list(self.results)