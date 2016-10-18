# -*- coding: utf-8 -*-

import json
import os.path
import random
import re

from flask import Flask, send_from_directory
from flask import request, abort

from flaskrun.flaskrun import flask_run
import datab.social_database as db

app = Flask(__name__)

# Regular expression to only accept certain files
fileChecker = re.compile(r"(.*\.js|.*\.html|.*\.png|.*\.css|.*\.map)$")
numberOfAnswers = 4

random.seed(7)


def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname(__file__))


@app.route('/')
def root():
    return index("index2.html")


@app.route('/<path:filename>')
def index(filename):
    if fileChecker.match(filename):
        return send_from_directory(os.path.join(root_dir(), 'static'), filename)
    abort(403)


@app.route('/register')
def register():
    # To obtain the mail
    email = request.args.get('email')
    print(email)
    if email is None:
        return json.dumps({})

    id_user = db.register_or_get_email(email)
    return json.dumps({"id": id_user})


@app.route('/join_room')
def join_room():
    room_id = request.args.get('room_id')
    email = request.args.get('email')
    user_id = db.register_or_get_email(email)
    db.exec_query("REPLACE INTO room_members (room_id, user_id) VALUES (%s,%s)", [room_id, user_id])
    return json.dumps({"id": user_id})


@app.route('/answered_room')
def answered_room():
    room_id = request.args.get('room_id')
    user_id = request.args.get('user_id')
    values = db.exec_query("SELECT a.id "
                           "FROM answer a INNER JOIN question q "
                           "WHERE a.question_id = q.id AND q.room_id = %s AND a.user_id= %s",
                           [room_id, user_id])
    return json.dumps({"answered": len(values) > 0})


@app.route('/get_user_id')
def get_user_id():
    email = request.args.get('email')
    id_user = db.register_or_get_email(email)
    return json.dumps({"id": id_user})


@app.route('/create_room')
def create_room():
    user_id = request.args.get('user_id')
    room_id = db.exec_query("INSERT INTO room (creator) VALUES (%s)", [user_id])
    return json.dumps({"id": room_id})


@app.route('/get_rooms')
def get_rooms():
    user_id = request.args.get('user_id')
    values = db.exec_query("SELECT r.id, r.status FROM room r WHERE r.creator=%s", [user_id])
    response = []
    for val in values:
        response.append({"id": val[0], "status": val[1]})
    return json.dumps(response)


@app.route('/fill_room', methods=['POST'])
def fill_room():
    json_data = request.get_json()
    if json_data is None:
        return json.dumps({"error": "no JSON found"})
    else:
        room_id = json_data["room_id"]
        questions = json_data["question"]
        for q in questions:
            db.exec_query("INSERT INTO question (room_id, question) VALUES (%s, %s)", [room_id, q])

        return json.dumps({"info": "Data received"})


@app.route('/open_room')
def open_room():
    room_id = request.args.get('room_id')
    print(room_id)
    db.exec_query("UPDATE room r SET r.status='started' WHERE r.id = %s", [room_id])
    return json.dumps({"info": "The room has been opened successfully", "status": "started"})


@app.route('/close_room')
def close_room():
    room_id = request.args.get('room_id')
    db.exec_query("UPDATE room  r SET r.status='closed' WHERE r.id = %s", [room_id])
    return json.dumps({"info": "The room has been closed successfully", "status": "closed"})


@app.route('/finish_room')
def finish_room():
    room_id = request.args.get('room_id')
    db.exec_query("UPDATE room  r SET r.status='finished' WHERE r.id = %s", [room_id])
    # for
    # SELECT id, COUNT(a.id), COUNT(a.id) FROM Room r INNER JOIN
    values = db.exec_query("SELECT u.email , COUNT(qq.id) "
                           "FROM quiz_question qq "
                           "INNER JOIN users u ON (qq.asked_user_id = u.id) "
                           "INNER JOIN room_members rm ON (u.id = rm.user_id) "
                           "WHERE qq.correct_answer_id = qq.answered_id AND rm.room_id = %s "
                           "GROUP BY u.email "
                           "ORDER BY COUNT(qq.id) DESC",
                           [room_id])
    ranking = []
    for row in values:
        ranking.append({"email": row[0], "correct": row[1]})

    return json.dumps({"ranking": ranking})


@app.route('/room_status')
def status_room():
    room_id = request.args.get('room_id')
    # SELECT status FROM Room WHERE id = 1
    values = db.exec_query("SELECT status FROM room WHERE id = %s", [room_id])
    return json.dumps({
        "status": values[0][0]
    })


@app.route('/get_room_questions')
def get_room_question():
    room_id = request.args.get('room_id')
    values = db.exec_query("SELECT id, question FROM question WHERE room_id = %s", [room_id])

    response = []
    for val in values:
        response.append({"id": val[0], "text": val[1]})

    return json.dumps({"questions": response})


@app.route('/post_room_answers', methods=['POST'])
def post_room_answers():
    json_data = request.get_json()
    if json_data is None:
        return json.dumps({"error": "no JSON found"}), 404
    user_id = json_data["user_id"]
    values = []
    for a in json_data["answers"]:
        values.append((a["id"], user_id, a["text"]))
        print(values[len(values) - 1])
    db.exec_many_query("INSERT INTO answer (question_id, user_id, answer) VALUES(%s,%s,%s)", values)
    return json.dumps({"info": "Data received"})


@app.route('/get_quiz_question')
def get_question():
    room_id = int(request.args.get('room_id'))
    user_id = int(request.args.get('user_id'))

    possible_questions = db.get_non_answered_questions(room_id, user_id)
    possible_users_to_ask = db.get_non_answered_people(room_id, user_id)

    question_id = []
    asked_about_id = []

    if len(possible_questions) > 0:
        question_id = random.sample(possible_questions, 1)
    else:
        possible_questions = db.get_all_questions(room_id)
        if len(possible_questions) > 0:
            question_id = random.sample(possible_questions, 1)
    if len(possible_users_to_ask) > 0:
        asked_about_id = random.sample(possible_users_to_ask, 1)
    else:
        possible_users_to_ask = db.get_all_different_people(room_id, user_id)
        if len(possible_questions) > 0:
            asked_about_id = random.sample(possible_users_to_ask, 1)

    if len(question_id) > 0 and 0 < len(asked_about_id):
        quiz_question_id = db.insert_quiz_question(user_id, asked_about_id[0], question_id[0])

        other_users = db.get_all_different_people(room_id, asked_about_id[0])
        random.shuffle(other_users)

        answers = []
        (answer_id, text_id) = db.get_answer(question_id[0], asked_about_id[0])

        db.exec_query("UPDATE quiz_question SET correct_answer_id=%s WHERE id = %s", [answer_id, quiz_question_id])

        answers.append((answer_id, text_id))
        if min(numberOfAnswers - 1, len(other_users)) > 0:
            for i in range(min(numberOfAnswers - 1, len(other_users))):
                (answer_id, text_id) = db.get_answer(question_id[0], other_users[i])
                answers.append((answer_id, text_id))

        # if commented the first answer will be the correct one
        random.shuffle(answers)

        answer_json = []
        for (answer_id, text_id) in answers:
            answer_json.append({"id": answer_id, "text": text_id})

        print(quiz_question_id)
        # SELECT 'question' FROM 'Question' WHERE 'id' = 3
        value = db.exec_query("SELECT id "
                              "FROM quiz_question "
                              "WHERE asked_user_id = %s AND about_user_id = %s AND question_id = %s",
                              [user_id, asked_about_id[0], question_id[0]])
        quiz_question_id = value[0][0]

        value = db.exec_query("SELECT q.question "
                              "FROM question q "
                              "WHERE q.id = %s",
                              [question_id[0]])

        question_text = value[0][0]

        value = db.exec_query("SELECT u.email "
                              "FROM users u "
                              "WHERE u.id=%s",
                              [asked_about_id[0]])
        user_name = value[0][0]

        question_text = "What did %s answer to '%s' ?" % (user_name, question_text)

        return json.dumps({
            "id":       quiz_question_id,
            "question": question_text,
            "answers":  answer_json
        })
    else:
        return json.dumps({"error": "Not available questions for this user in this room"})


@app.route('/post_quiz_answer')
def post_answer():
    quiz_question_id = request.args.get('quiz_question_id')
    quiz_answer_id = request.args.get('quiz_answer_id')

    db.exec_query("UPDATE quiz_question SET answered_id = %s WHERE id = %s", [quiz_answer_id, quiz_question_id])

    value = db.exec_query("SELECT qq.answered_id, qq.correct_answer_id, qq.question_id  "
                          "FROM quiz_question qq "
                          "WHERE qq.id = %s", [quiz_question_id])

    answered_id = value[0][0]
    correct_answer_id = value[0][1]
    question_id = value[0][2]

    value = db.exec_query("SELECT a.answer FROM answer a WHERE a.id = %s ", [correct_answer_id])

    if len(value) > 0:
        text = value[0][0]
    else:
        text = "something when wrong"

    if value is None:
        return json.dumps({"error": "Internal server error"})
    return json.dumps({
        "correct":       answered_id == correct_answer_id,
        "question":      question_id,
        "correct_answer": {"id": correct_answer_id, "text": text}
    })


if __name__ == '__main__':
    flask_run(app)
