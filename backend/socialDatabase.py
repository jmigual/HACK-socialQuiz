import MySQLdb
import MySQLdb.connections

DB_HOST = 'localhost'
DB_USER = 'socialuser'
DB_PASS = '12345678'
DB_NAME = 'social_quiz'


def get_connection():
	return MySQLdb.connect(*[DB_HOST, DB_USER, DB_PASS, DB_NAME])


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
	conn = get_connection()
	curs = conn.cursor()
	print(email)
	curs.execute("SELECT id FROM User WHERE email = %s", [email])
	value = curs.fetchall()
	if len(value) <= 0:
		curs.execute("INSERT INTO User (email) VALUES (%s)", [email])
		value = conn.insert_id()
		conn.commit()
	else:
		value = value[0][0]
	curs.close()
	conn.close()
	print(value)
	return value
