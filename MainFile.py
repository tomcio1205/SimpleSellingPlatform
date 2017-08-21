# -*- coding: utf-8 -*-
import json
from DBConnection.DatabaseConnection import PostgresConnection
from flask import Flask, request
from Config.DBConfig import database_parameters
app = Flask(__name__)
PER_PAGE = 5



@app.route('/getallproducts/', defaults={'page': 1, 'catchall': ''})
@app.route('/getallproducts/page/<int:page>', defaults={'catchall': ''})
@app.route('/getallproducts/page/<int:page>/<path:catchall>')
@app.route('/getallproducts/<path:catchall>', defaults={'page': 1})
def get__all_products(page, catchall):
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


# @app.route('/getproducts/', defaults={'page': 1})
# @app.route('/getproducts/page/<int:page>')
# def get__all_products(page):
# 	query = "select image, title, description,product_value,curency_unit,comments,likes," \
# 	        " category_id from products order by category_id"
#
# 	result = execute_query(query)
# 	ret = Pagination(page, 1, result).iter_pages()
#
# 	return ret


@app.route('/productdetails/<string:product_id>')
def get_product(product_id):
	query = 'select title, image, description, product_value, curency_unit, comments, likes from products' \
	        ' where id = {id}'.format(id=product_id)

	ret = execute_query(query)

	return ret


@app.route('/createorder', methods=['POST'])
def create_order():
	"""
	Receive simple json:
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
	query = "insert into orders (user_id, delivery_type_id, description, total_price, product_counts_sum)" \
	        " values (%(user)s, %(delivery_type)s, %(description)s, %(total_price)s, %(prduct_counts)s) RETURNING id"
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
	# I assume that user wish list will by sent as json type
	data = json.loads(request.content.read())


########AUTH########


def execute_query(query, args=()):
	db_param = database_parameters()
	with PostgresConnection(db_param, query, args) as ps:
		return ps


class Pagination(object):
	def __init__(self, page, per_page, result):
		self.page = page
		self.per_page = per_page
		self.result = result

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
		# return list_pag


if __name__ == '__main__':
	app.run('0.0.0.0', 8080)
