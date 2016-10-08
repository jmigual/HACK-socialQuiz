import pymysql

DB_HOST = 'localhost'
DB_USER = 'socialuser'
DB_PASS = '12345678'
DB_NAME = 'social_quiz'


def get_connection():
	return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, db=DB_NAME)


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


def exec_many_query(query, values):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.executemany(query, values)
	conn.commit()
	cursor.close()
	conn.close()

def register_or_get_email(email):
	# Create new connection/cursor
	value = exec_query("SELECT id FROM Users WHERE email = %s", [email])
	if len(value) <= 0:
		value = exec_query("INSERT INTO Users (email) VALUES (%s)", [email])
	else:
		value = value[0][0]
	return value

def getNonAnsweredQuestions(idRoom,idUser):
    return [3,4,5,6]
    
def getNonAnsweredPeople(idRoom,idUser):
    return [8,2]
    
def getAllQuestions(idRoom):
    #SELECT `id` FROM `question` WHERE `roomId` = roomId
    ret = []
    value = exec_query("SELECT 'id' FROM 'question' WHERE 'roomId' = %d", [idRoom])
    for row in value:
        ret.append(row[0])
    return ret
    
def getAllDifferentPeople(idRoom,idUser):
    return [1,2,3,4,5,6,7]
    
def insertQuizQuestion(idRoom,idUser,askedAboutId,questionId):
    
    return 3
    
def getAnswer(questionId,userId):
    value = exec_query("SELECT 'id','answer' FROM 'answer' WHERE 'questionId' = %d AND 'userId' = %d", [questionId,userId])
    if len(value) != 1:
        return (404, "Answer not found")
    return (value[0][0],value[0][1])
