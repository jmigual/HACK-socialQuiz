import MySQLdb

DB_HOST = 'localhost'
DB_USER = 'socialuser'
DB_PASS = '12345678'
DB_NAME = 'social_quiz'


def get_connection():
	return MySQLdb.connect(*[DB_HOST, DB_USER, DB_PASS, DB_NAME])


def get_cursor():
	return get_connection().cursor()


def run_query(query=''):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute(query)

	if query.upper().startswith('SELECT'):
		data = cursor.fetchall()
	else:
		conn.commit()
		data = None

	cursor.close()
	conn.close()

	return data


def register_or_get_email(email):
	curs = get_cursor()
	curs.execute("SELECT * FROM User WHERE email = %s", email)
