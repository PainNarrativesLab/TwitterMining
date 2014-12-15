import couchdb


class CouchDAO:
	def __init__(self, server='http://localhost:5984'):
		self.server = couchdb.Server(server)
	
	def connect(self, database_name):
		"""
		Connects to couchdb database
		@param database_name The name of the database to connect to
		@type database_name string
		"""
		try:
			self.db = self.server.create(database_name)
		except couchdb.http.PreconditionFailed, e:
			self.db = self.server[database_name]
		return self.db

	def get_all_ids(self):
		"""
		Gets all documentids from db; ignores the _design/index file
		"""
		q = []
		for id in self.db:
			q.append(id)
		self.ids = []
		[self.ids.append(i) for i in q if i != '_design/index'] #First id returned is the design document