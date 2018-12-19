import pymysql
from pprint import pprint
from ipdb import set_trace
import datetime

def get_db():
	user = 'root'
	password = '1998218wrh'
	db = 'SAKILA'
	host = 'localhost'
	conn = pymysql.connect(host, user, password, db)
	db = conn.cursor(pymysql.cursors.DictCursor)

	return conn, db

def calc_hot():
	conn, db = get_db()
	db.execute(
		'SELECT p.id, p.num_view, p.num_reply, p.created'
		' FROM post p JOIN user u ON p.author_id = u.id'
		' ORDER BY created DESC'
	)
	posts = db.fetchall()

	today = datetime.datetime.today()
	hr = today.hour
	day = today.day
	month = today.month
	year = today.year
	for post in posts:
		num_view = post['num_view']
		num_reply = post['num_reply']
		created_time = post['created']
		delta = (((year - today.year) * 12 + (month - created_time.month)) * 30 + (day - created_time.day)) * 24 + hr - created_time.hour
		hot = float(num_view + num_reply + 1) / ((delta + 2) ** 1.8)
		'''print(delta)
		print(num_view + num_reply)
		print("hot = ", hot)
		print()'''

		db.execute(
			'UPDATE post SET hot = %s'
			' WHERE id = %s',
			(str(hot), post['id'])
		)
		conn.commit()

		#set_trace()



	#posts = sorted(posts, key=lambda p: p['created'], reverse=False)

	#pprint(posts)
