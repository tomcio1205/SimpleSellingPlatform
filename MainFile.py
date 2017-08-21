# -*- coding: utf-8 -*-
import json
from DBConnection.DatabaseConnection import PostgresConnection
from flask import Flask, request, Response
from Config.DBConfig import database_parameters
from functools import wraps
import hashlib
import stripe

stripe.api_key = "sk_test_BQokikJOvBiI2HlWgH4olfQ2"

app = Flask(__name__)
PER_PAGE = 5


def encode_pswd(password):
	salt = "md5".encode('utf-8')
	m = hashlib.md5()
	m.update(salt + password.encode('utf-8'))
	pswd = m.hexdigest()
	return pswd


def check_auth(username, password):
	"""This function is called to check if a username /
    password combination is valid.
    """
	pswd = encode_pswd(password)
	query = "Select email, password from users where email = '{}'".format(username)
	ret = execute_query(query)
	try:
		user_param = json.loads(ret)[0]
	except json.decoder.JSONDecodeError:
		return False

	return username == user_param['email'] and pswd == user_param['password']


def authenticate():
	"""Sends a 401 response that enables basic auth"""
	return Response(
		'Could not verify your access level for that URL.\n'
		'You have to login with proper credentials', 401,
		{'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth = request.authorization
		if not auth or not check_auth(auth.username, auth.password):
			return authenticate()
		return f(*args, **kwargs)

	return decorated


@app.route('/createuser', methods=['POST'])
def create_user():
	received_data = json.loads(request.data)
	description = "Customer for {email}".format(email=received_data['email'])
	x_strp = stripe.Customer.create(
	  description=description,
	  source="tok_amex" # obtained with Stripe.js
	)
	pswd = encode_pswd(received_data['password'])
	received_data['password'] = pswd
	received_data['stripe_id'] = x_strp['id']
	query = "insert into users (first_name, last_name, email, phone_number, password, user_type_id, stripe_id)" \
	        " values (%(first_name)s, %(last_name)s, %(email)s, %(phone_number)s, %(password)s," \
	        " %(user_type_id)s, %(stripe_id)s) RETURNING id"
	ret = execute_query(query, received_data)
	try:
		json.loads(ret)[0]['id']
	except json.decoder.JSONDecodeError:
		return "Insert into order_details failed"
	return "Success"


@app.route('/getallproducts/', defaults={'page': 1, 'catchall': ''})
@app.route('/getallproducts/page/<int:page>', defaults={'catchall': ''})
@app.route('/getallproducts/page/<int:page>/<path:catchall>')
@app.route('/getallproducts/<path:catchall>', defaults={'page': 1})
def get__all_products(page, catchall):
	"""
	Get all products (with pagination). Example call:
	/getallproducts/ : no filter and title - return all products
	/getallproducts/page/2: next page of products
	/getallproducts/filterby=Food: get all products of food category
	/getallproducts/filterby=Food%title=Milk: get all products of food category with milk in title
	:param page:
	:param catchall:
	:return:
	"""
	product_option = {}

	for el in catchall.split('%'):
		if 'title' in el:
			product_option['title'] = el.split('=')[1]
		if 'filterby' in el:
			product_option['category'] = el.split('=')[1]

	if len(product_option) == 2:
		query = "select p.image,p.title,p.description,p.product_value,p.curency_unit,p.comments,likes," \
		        "c.title from products p left join category c on p.category_id=c.id " \
		        "where c.title like %(category)s and p.title like %(title)s"
	elif len(product_option) == 1 and 'title' in product_option:
		query = "select image, title, description,product_value,curency_unit,comments,likes," \
		        " category_id from products where title like %(title)s"
	elif len(product_option) == 1 and 'category' in product_option:
		query = "select p.image,p.title,p.description,p.product_value,p.curency_unit,p.comments,likes," \
		        "p.title from products p left join category c on p.category_id=c.id " \
		        "where c.title like %(category)s"
	else:
		query = "select image, title, description,product_value,curency_unit,comments,likes," \
		        " category_id from products"

	result = execute_query(query, product_option)

	ret = Pagination(page, PER_PAGE, result).iter_pages()

	return ret


@app.route('/productdetails/<string:product_id>')
def get_product(product_id):
	"""
	Function that return details of product
	:param product_id: eg. 2
	:return: json in str type
	"""
	query = 'select title, image, description, product_value, curency_unit, comments, likes from products' \
	        ' where id = {id}'.format(id=product_id)

	ret = execute_query(query)

	return ret


@app.route('/createorder', methods=['POST'])
@requires_auth
def create_order():
	"""
    Example received json:
    {
    "user": 3,
    "total_price": 1234,
    "delivery_type": 1,
    "description": "send as soon as possible",
    "prduct_counts": 4,
    "data": [
        {
            "product_id": 2,
            "product_count": 2
        },
        {
            "product_id": 3,
            "product_count": 2
        }

        ]
    }
    :return:
    """

	received_data = json.loads(request.data)
	x_strp = stripe.Charge.create(
		amount=int(received_data['total_price'])*118, #integer only? #TODO 50 cents minimum
		currency="eur", #TODO
		description="Charge for user_id = {}".format(received_data['user']), #TODO get user mail?
		source="tok_visa", # obtained with Stripe.js
		idempotency_key='3ylzJDWar4cpm3F2' #TODO generating key
	)
	received_data['stripe_id'] = x_strp['id']
	query = "insert into orders (user_id, delivery_type_id, description, total_price, product_counts_sum, stripe_id)" \
	        " values (%(user)s, %(delivery_type)s, %(description)s, %(total_price)s, %(prduct_counts)s, %(stripe_id)s) RETURNING id"
	ret = execute_query(query, received_data)
	try:
		json.loads(ret)[0]['id']
	except json.decoder.JSONDecodeError:
		return "Insert into order failed"
	for data in received_data['data']:
		query_details = "insert into order_details (product_id, product_counts, order_id)" \
		                " values (%(product_id)s, %(product_count)s, {order_id}) RETURNING id".format(
			order_id=json.loads(ret)[0]['id'])
		ret_details = execute_query(query_details, data)
		try:
			json.loads(ret_details)[0]['id']
		except json.decoder.JSONDecodeError:
			return "Insert into order_details failed"
	return "Success"


@app.route('/userwishlist', methods=['POST'])
def user_wishlist(request):
	"""
	USER WISH LIST ???
	:param request:
	:return:
	"""
	pass


def execute_query(query, args=()):
	"""
	Call query on database
	:param query: "Select * from users where id = %(id)s"
	:param args: {id: 1}
	:return: json in str type
	"""
	db_param = database_parameters()
	with PostgresConnection(db_param, query, args) as ps:
		return ps


class Pagination(object):
	"""
	Simple class tha paginate received records
	"""
	def __init__(self, page, per_page, result):
		self.page = page
		self.per_page = per_page
		self.result = result

	def __repr__(self):
		return "Class name {}".format(self.__class__.__name__)

	def iter_pages(self):
		try:
			list_pag = json.loads(self.result)
		except json.decoder.JSONDecodeError:
			return 0
		page_list = []
		total = len(list_pag)
		for iter in range((self.page - 1) * self.per_page, (self.page * self.per_page)):
			if iter >= total:
				break
			page_list.append(list_pag[iter])
		return json.dumps(page_list, default=PostgresConnection.decimal_default)


if __name__ == '__main__':
	app.run('0.0.0.0', 8080)
