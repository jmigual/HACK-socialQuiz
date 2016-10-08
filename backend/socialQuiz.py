# -*- coding: utf-8 -*-

import json
import random

from flask import Flask
from flask import request

import datab.socialDatabase as db

app = Flask(__name__)
numberOfAnswers = 4

random.seed(7)


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
    json_data = request.get_json()
    if json_data is None:
        return "Error: no JSON found"
    else:
        room_id = json_data["id"]
        questions = json_data["question"]

        for q in questions:
            db.exec_query("INSERT INTO Question (roomId, question) VALUES (%s, %s)", [room_id, q])

        return "Data received"


@app.route('/getRoomQuestion')
def get_room_question():
    id_room = request.args.get('idRoom')
    values = db.exec_query("SELECT id, question FROM Question WHERE roomId=%s", [id_room])

    response = []
    for val in values:
        response.append({"id": val[0], "text": val[1]})

    return json.dumps({"questions": response})


@app.route('/postRoomAnswers', methods=['POST'])
def post_room_answers():
    json_data = request.get_json()
    if json_data is None:
        print("no json");
        return "Error: no JSON found"
    else:
        user_id = json_data["idUser"]
        values = []
        for a in json_data["answers"]:
            values.append((a["id"], user_id, a["text"]))
            print(values[len(values) - 1])
        db.exec_many_query("INSERT INTO Answer (questionId, userId, answer) VALUES(%s,%s,%s)", values)
        return "Data received"


@app.route('/getQuizQuestion')
def get_question():
    idRoom = request.args.get('idRoom')
    idUser = request.args.get('idUser')
    
    possibleQuestions = db.getNonAnsweredQuestions(idRoom,idUser)
    possibleUsersToAsk = db.getNonAnsweredPeople(idRoom,idUser)
    
    if len(possibleQuestions) > 0:
        questionId = random.sample(possibleQuestions,1)
    else :
        possibleQuestions = db.getAllQuestions(idRoom)
        questionId = random.sample(possibleQuestions,1)
    if len(possibleUsersToAsk) > 0:
        askedAboutId = random.sample(possibleUsersToAsk,1)
    else :
        possibleUsersToAsk = db.getAllDifferentPeople(idRoom,idUser)
        askedAboutId = random.sample(possibleUsersToAsk,1)
    
    
    quizQuestionId = db.insertQuizQuestion(idRoom,idUser,askedAboutId,questionId)
    
    otherUsers = db.getAllDifferentPeople(idRoom,askedAboutId)
    
    random.shuffle(otherUsers)
    
    
    answers = []
    (answerId,textId) = db.getAnswer(questionId,askedAboutId)
    answers.append((answerId,textId))    
    for i in range(numberOfAnswers-1) :
        (answerId,textId) = db.getAnswer(questionId,otherUsers[i])
        answers.append((answerId,textId))
    
    #if commented the first answer will be the correct one
    #random.shuffle(answers)
    
    
    answerJson = []
    for (answerId,textId) in answers:
        answerJson.append({"id": answerId ,"text":textId})
    
    return json.dumps({
          "id": quizQuestionId,
          "question": "Whats your age?",
          "answers": answerJson
        })


@app.route('/postAnswer')
def post_answer():
    quizQuestionId = request.args.get('quizQuestionId')
    answerId = request.args.get('answerId')

    value = db.exec_query("SELECT qq.answerId, q.question, a.answer AS RightAnswer "
                          "FROM QuizQuestion qq "
                          "INNER JOIN Answer a ON (qq.answerId = a.id) "
                          "INNER JOIN Question q ON (q.id = a.questionId) "
                          "WHERE qq.id = %s", [quizQuestionId])
    if value is None:
        return "Internal server error"
    return json.dumps({
          "correct": value[0] == answerId,
          "question": value[1],
          "correctAnswer": {"id": value[0], "text": value[2]}
        })

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
