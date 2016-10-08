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


def exec_query(query, bind_values):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute(query, bind_values)

	if query.upper().startswith('SELECT'):
		data = cursor.fetchall()
	elif query.upper().startswith('INSERT'):
		data = conn.insert_id()
		conn.commit()
	else:
		conn.commit()
		data = None
	cursor.close()
	conn.close()
	return data


def register_or_get_email(email):
	# Create new connection/cursor
	value = exec_query("SELECT id FROM Users WHERE email = %s", [email])
	if len(value) <= 0:
		value = exec_query("INSERT INTO Users (email) VALUES (%s)", [email])
	else:
		value = value[0][0]
	return value

