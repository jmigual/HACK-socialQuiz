import pymysql
import json


class Credentials:
    __json_credentials = None

    @classmethod
    def get_credentials(cls):
        if cls.__json_credentials is None:
            f = open('credentials.json', 'r')
            cls.__json_credentials = json.load(f)
        return cls.__json_credentials


def get_connection():
    cred = Credentials.get_credentials()
    return pymysql.connect(host=cred["host"], user=cred["user"], password=cred["password"], db=cred["db"])


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
    value = exec_query("SELECT id FROM users WHERE email = %s", [email])
    if len(value) <= 0:
        value = exec_query("INSERT INTO users (email) VALUES (%s)", [email])
    else:
        value = value[0][0]
    return value


def get_non_answered_questions(id_room, id_user):
    ret = []
    value = exec_query("SELECT DISTINCT q.id "
                       "FROM question q "
                       "WHERE q.room_id = %s AND NOT EXISTS ( "
                       "  SELECT qq.question_id "
                       "  FROM quiz_question qq "
                       "  WHERE q.id = qq.question_id AND qq.asked_user_id = %s)",
                       [id_room, id_user])
    for row in value:
        ret.append(row[0])
    # print("getNonAnsweredQuestions");
    #    print(ret);
    return ret


def get_non_answered_people(id_room, id_user):
    ret = []
    value = exec_query("SELECT DISTINCT rm.user_id "
                       "FROM room_members rm "
                       "WHERE rm.room_id = %s AND rm.user_id <> %s AND NOT EXISTS ( "
                       "  SELECT qq.about_user_id "
                       "  FROM quiz_question qq "
                       "  WHERE rm.user_id = qq.about_user_id AND qq.asked_user_id = %s)",
                       [id_room, id_user, id_user])
    for row in value:
        ret.append(row[0])
    # print("getNonAnsweredPeople");
    #    print(ret);
    return ret


def get_all_questions(id_room):
    ret = []
    value = exec_query("SELECT 'id' FROM Question WHERE 'roomId' = %s", [id_room])
    for row in value:
        ret.append(row[0])
    return ret


def get_all_different_people(id_room, id_user):
    ret = []
    value = exec_query("SELECT DISTINCT rm.user_id "
                       "FROM room_members rm "
                       "WHERE rm.room_id = %s AND rm.user_id <> %s",
                       [id_room, id_user])
    for row in value:
        ret.append(row[0])
    return ret


def insert_quiz_question(id_user, asked_about_id, question_id):
    value = exec_query("INSERT INTO quiz_question ( asked_user_id, about_user_id, question_id) "
                       "VALUES (%s,%s,%s)",
                       [id_user, asked_about_id, question_id])
    return value


def get_answer(question_id, user_id):
    print("getAnswer")
    print(question_id)
    print(user_id)
    value = exec_query("SELECT a.id, a.answer "
                       "FROM answer a "
                       "WHERE a.question_id = %s AND a.user_id = %s", [question_id, user_id])
    print("getAnswer")
    print(value)
    if len(value) != 1:
        return 404, "Answer not found"
    return value[0][0], value[0][1]
