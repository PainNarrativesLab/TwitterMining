#Don't forget to start server
#redis-server /usr/local/etc/redis.conf
#install pip install hiredis
import redis

class RedisDAO:
	"""
	Creates connection to redis host. Base class for redis services. Should not be directly called.
	"""
	def __init__(self, host='localhost', port=6379, db=0):
		d = str(db)
		#self.dbindex = 0
		self.dbindex = 'db%s' %d 
		self.db = redis.Redis(host=host, port=port, db=db)
	
	def delete_all_databases(self):
	#	self.flushall()
		pass
	
#def get_size(self):
#self.info = self.db.info()
#d = str(self.dbindex)
#s = self.info[d]
#return self.info['db0']
