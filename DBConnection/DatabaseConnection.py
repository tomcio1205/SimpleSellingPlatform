import psycopg2
import json
import decimal
import datetime

class PostgresConnection:
	"""
	Class for postgres connection
	Result are returning in json type
	"""

	def __init__(self, db_param={}, query='', args=()):
		self.database_name = db_param['db_name']
		self.user = db_param['db_user']
		self.password = db_param['db_password']
		self.host = db_param['db_host']
		self.port = db_param['db_port']
		self.query = query
		self.args = args

	def __exit__(self, *args):
		if self.conn:
			self.conn.close()

	def __enter__(self):
		self.conn = None
		try:
			self.conn = psycopg2.connect(database=self.database_name, user=self.user, password=self.password,
			                             host=self.host, port=self.port)
			cur = self.conn.cursor()
			cur.execute(self.query, self.args)
			self.conn.commit()
		except psycopg2.Error as e:
			if self.conn:
				self.conn.rollback()
			return e.pgerror
		try:
			ret = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
			json_result = json.dumps(ret, default=self.decimal_default)
			return json_result
		except psycopg2.ProgrammingError as e:
			return e

	def __repr__(self):
		return "Class Name: {self.__class__.__name__}".format(self=self)

	def decimal_default(self, obj):
		if isinstance(obj, decimal.Decimal):
			return float(obj)
		elif isinstance(obj, datetime.datetime):
			return str(obj)
		raise TypeError

