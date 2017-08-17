from twisted.internet import reactor, endpoints
from klein import Klein
from DatabaseConnection import PostgresConnection


class HttpRest(object):
	app = Klein()
	pass


def execute_query(query):
	with PostgresConnection('smartbox_database_uuid', 'postgres', 'postgres', '127.0.0.1', '5432', query) as ps:
		return ps

if __name__ == '__main__':
	query2 = 'Select * from device'
	x = execute_query(query2)
	print(x)
