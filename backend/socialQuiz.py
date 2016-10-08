# -*- coding: utf-8 -*-

from flask import Flask, send_from_directory
from flask import request
import json
import backend.socialDatabase as db

app = Flask(__name__)


@app.route('/')
def index():
    return "Hello world"


@app.route('/register')
def register():
    # To obtain the mail
    email = request.args.get('email')
    print(email)
    if email is None:
        return json.dumps({})

    id_user = db.register_or_get_email(email)
    return json.dumps({"id": id_user})


@app.route('/joinRoom')
def join_room():
    _ = request.args.get('idRoom')
    email = request.args.get('email')
    id_user = db.register_or_get_email(email)
    return json.dumps({"id": id_user})


@app.route('/getUserId')
def get_user_id():
    email = request.args.get('email')
    id_user = db.register_or_get_email(email)
    return json.dumps({"id": id_user})


@app.route('/createRoom')
def create_room():
    user_id = request.args.get('userId')
    room_id = db.exec_query("INSERT INTO Room (creator) VALUES (%s)", [user_id])

    return json.dumps({"id": room_id})


@app.route('/fillRoom', methods=['POST'])
def fill_room():
    json_data = request.get_json(force=True)
    if json_data is None:
        return "Error: no JSON found"
    else:
        room_id = json_data["id"]
        questions = json_data["question"]

        for q in questions:
            db.exec_query("INSERT INTO Question (roomId, question) VALUES (%s, %s)", room_id, q)

        return "Data received"


@app.route('/getRoomQuestion')
def get_room_question():
    idRoom = request.args.get('idRoom')
    return json.dumps({"questions": [
        {"id": 2113, "text": "How do you feel?"},
        {"id": 2114, "text": "Do you want a kiss?"}]})


@app.route('/postRoomAnswers')
def post_room_answers():
    print(request.form())


@app.route('/getQuizQuestion')
def get_question():
    idRoom = request.args.get('idRoom')
    idUser = request.args.get('idUser')
    return json.dumps({
          "id": 1234,
          "question": "Whats your age?",
          "answers": [{"id": 34,"text":"Ans1"}, {"id": 35, "text": "Ans2"}]
        })


@app.route('/postAnswer')
def post_answer():
    quizQuestionId = request.args.get('quizQuestionId')
    answerId = request.args.get('answerId')
    return json.dumps({
          "correct": "false",
          "question": "Whats your age?",
          "correctAnswer": {"id": 34, "text": "Ans1"}
        })

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
