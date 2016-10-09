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
    idRoom = request.args.get('idRoom')
    email = request.args.get('email')
    id_user = db.register_or_get_email(email)
    db.exec_query("REPLACE INTO RoomMembers (roomId, userId) VALUES (%s,%s)", [idRoom, id_user])
    return json.dumps({"id": id_user})
    
@app.route('/answeredRoom')
def answered_room():
    idRoom = request.args.get('idRoom')
    user_id = request.args.get('userId')
    values = db.exec_query("SELECT a.id FROM answer a INNER JOIN question q WHERE a.questionId = q.id AND q.roomId = %s AND a.userId= %s",[idRoom,user_id]);
    #return json.dumps(values)
    return json.dumps({"answered": len(values) > 0 })
    
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

@app.route('/getRooms')
def get_rooms():
    user_id = request.args.get('userId');
    values = db.exec_query("SELECT id FROM Room WHERE creator=%s",[user_id]);
    response=[];
    for val in values:
        response.append(val[0]);
    return json.dumps({"rooms": response})


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

        
        
@app.route('/openRoom')
def open_room():
    id_room = request.args.get('id')
    values = db.exec_query("UPDATE Room r SET r.status='started' WHERE r.id = %s", [id_room])
    return "status='started'"

@app.route('/closeRoom')
def close_room():
    id_room = request.args.get('id')
    values = db.exec_query("UPDATE Room  r SET r.status='closed' WHERE r.id = %s", [id_room])
    return "status='closed'"
    
@app.route('/finishRoom')
def finish_room():
    id_room = request.args.get('id')
    values = db.exec_query("UPDATE Room  r SET r.status='finished' WHERE r.id = %s", [id_room])
    ranking = []
    #for
    #SELECT id, COUNT(a.id), COUNT(a.id) FROM Room r INNER JOIN
    values = db.exec_query("SELECT qq.askedUserId, COUNT(qq.id) FROM quizquestion qq WHERE qq.correctanswerId = qq.answeredId")
    #SELECT qq.askedUserId, COUNT(qq.id) FROM quizquestion qq WHERE qq.correctanswerId = qq.answeredId
    return return json.dumps(values)

@app.route('/statusRoom')
def status_room():
    id_room = request.args.get('id')
    #SELECT status FROM Room WHERE id = 1
    values = db.exec_query("SELECT status FROM Room WHERE id = %s", [id_room])
    return json.dumps({
          "status": values[0][0] 
        })


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
    idRoom = int(request.args.get('idRoom'))
    idUser = int(request.args.get('idUser'))
    
    possibleQuestions = db.getNonAnsweredQuestions(idRoom,idUser)
    possibleUsersToAsk = db.getNonAnsweredPeople(idRoom,idUser)
    
    questionId = -1
    askedAboutId = -1
    
    if len(possibleQuestions) > 0:
        questionId = random.sample(possibleQuestions,1)
    else :
        possibleQuestions = db.getAllQuestions(idRoom)
        if len(possibleQuestions) > 0:
            questionId = random.sample(possibleQuestions,1)
    if len(possibleUsersToAsk) > 0:
        askedAboutId = random.sample(possibleUsersToAsk,1)
    else :
        possibleUsersToAsk = db.getAllDifferentPeople(idRoom,idUser)
        if len(possibleQuestions) > 0:
            askedAboutId = random.sample(possibleUsersToAsk,1)
    
    print(questionId);
    if 0 < questionId and 0 < askedAboutId :
        quizQuestionId = db.insertQuizQuestion(idUser,askedAboutId,questionId)
        
        otherUsers = db.getAllDifferentPeople(idRoom,askedAboutId)
        
        random.shuffle(otherUsers)
        
        
        answers = []
        (answerId,textId) = db.getAnswer(questionId,askedAboutId)
        answers.append((answerId,textId))
        for i in range( max(numberOfAnswers-1) , len(otherUsers) ):
            (answerId,textId) = db.getAnswer(questionId,otherUsers[i])
            answers.append((answerId,textId))
        
        #if commented the first answer will be the correct one
        #random.shuffle(answers)
        
        
        answerJson = []
        for (answerId,textId) in answers:
            answerJson.append({"id": answerId ,"text":textId})
            
        #SELECT 'question' FROM 'Question' WHERE 'id' = 3
        value = exec_query("SELECT 'question' FROM 'Question' WHERE 'id' = %s", [quizQuestionId])
        question = value[0]
        
        return json.dumps({
              "id": quizQuestionId,
              "question": question,
              "answers": answerJson
            })
    else:
        return "Not info found in  DB"


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
