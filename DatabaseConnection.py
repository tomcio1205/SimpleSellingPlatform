import psycopg2


class PostgresConnection:
	"""
	class for postgres connection
	"""

	def __init__(self, database_name, user, password, host, port, query):
		self.database_name = database_name
		self.user = user
		self.password = password
		self.host = host
		self.port = port
		self.query = query

	def __exit__(self, *args):
		self.conn.commit()
		self.conn.close()

	def __enter__(self):
		self.conn = psycopg2.connect(database=self.database_name, user=self.user, password=self.password,
		                             host=self.host, port=self.port)
		cur = self.conn.cursor()
		cur.execute(self.query)
		rows = cur.fetchall()
		return rows

	def __repr__(self):
		return "Class Name: {self.__class__.__name__}".format(self=self)

