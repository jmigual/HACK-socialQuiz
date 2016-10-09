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
#SELECT DISTINCT q.id
#FROM Question q
#WHERE q.roomId =3
#AND NOT 
#EXISTS (
#SELECT qq.questionId
#FROM QuizQuestion qq
#WHERE q.id = qq.questionId
#AND qq.askedUserId = 2
    ret = []
    value = exec_query("SELECT DISTINCT q.id FROM Question q WHERE q.roomId = %s AND NOT EXISTS ( SELECT qq.questionId FROM QuizQuestion qq WHERE q.id = qq.questionId AND qq.askedUserId = %s)", [idRoom, idUser])
    for row in value:
        ret.append(row[0])
    print("getNonAnsweredQuestions");
    print(ret);
    return ret


def getNonAnsweredPeople(idRoom,idUser):
# SELECT DISTINCT rm.userId FROM RoomMembers rm WHERE rm.roomId = 3 AND NOT EXISTS ( SELECT qq.aboutUserId FROM QuizQuestion qq WHERE rm.userId = qq.aboutUserId AND qq.askedUserId =  2)
    ret = []
    value = exec_query("SELECT DISTINCT rm.userId FROM RoomMembers rm WHERE rm.roomId = %s AND NOT EXISTS ( SELECT qq.aboutUserId FROM QuizQuestion qq WHERE rm.userId = qq.aboutUserId AND qq.askedUserId = %s)", [idRoom, idUser])
    for row in value:
        ret.append(row[0])
    print("getNonAnsweredPeople");
    print(ret);
    return ret


def getAllQuestions(idRoom):
    #SELECT `id` FROM `question` WHERE `roomId` = roomId
    ret = []
    value = exec_query("SELECT 'id' FROM Question WHERE 'roomId' = %s", [idRoom])
    for row in value:
        ret.append(row[0])

    print("getAllDifferentPeople");
    print(ret);
    return ret


def getAllDifferentPeople(idRoom,idUser):
    ret = []
    value = exec_query("SELECT DISTINCT rm.userId FROM RoomMembers rm WHERE rm.roomId = %s AND  rm.userId != %s", [idRoom, idUser])
    for row in value:
        ret.append(row[0])
    print("getAllDifferentPeople");
    print(ret);
    return ret


def insertQuizQuestion(idUser,askedAboutId,questionId):
    value = exec_query("INSERT INTO QuizQuestion ( askedUserId, aboutUserId, questionId) VALUES (%s,%s,%s)", [idUser,askedAboutId,questionId])
    # SELECT `id` FROM `QuizQuestion` WHERE `askedUserId` = 3 AND `aboutUserId` = 4 and `questionId` = 5
    value = exec_query("SELECT id FROM QuizQuestion WHERE askedUserId = %s AND aboutUserId = %s and questionId = %s", [idUser,askedAboutId,questionId])
    print(value);
    return value[0]


def getAnswer(questionId,userId):
    print("getAnswer")
    print(questionId)
    print(userId)
    value = exec_query("SELECT a.id, a.answer "
                       "FROM Answer a "
                       "WHERE a.questionId = %s AND a.userId = %s", [questionId, userId])
    print("getAnswer")
    print(value)
    if len(value) != 1:
        return 404, "Answer not found"
    return value[0][0], value[0][1]
