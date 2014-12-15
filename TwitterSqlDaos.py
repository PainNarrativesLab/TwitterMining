import DAO

class TwitterSQLDAO(DAO.BaseDAO):
	"""
	Base database abstraction layer for twitter mysql database
	"""
	def __init__(self, test=False, local=True):
		if test == False:
			pass
				
		if test == False:	
			databaseName = 'twitter_data'
		else:
			databaseName = 'twitter_dataTEST'
		DAO.BaseDAO.__init__(self)
		if local == False:
			self.connectRemote(databaseName)
		else:
			self.connect(databaseName)

