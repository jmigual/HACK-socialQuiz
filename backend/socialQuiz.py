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
    values = db.exec_query("SELECT r.id, r.status FROM Room r WHERE r.creator=%s", [user_id]);
    response = [];
    for val in values:
        response.append({"id": val[0], "status": val[1]})
    return json.dumps(response)


@app.route('/fillRoom', methods=['POST'])
def fill_room():
    json_data = request.get_json()
    if json_data is None:
        return json.dumps({"error": "no JSON found"})
    else:
        room_id = json_data["id"]
        questions = json_data["question"]
        for q in questions:
            db.exec_query("INSERT INTO Question (roomId, question) VALUES (%s, %s)", [room_id, q])

        return json.dumps({"info": "Data received"})

        
@app.route('/openRoom')
def open_room():
    id_room = request.args.get('id')
    print(id_room)
    db.exec_query("UPDATE Room r SET r.status='started' WHERE r.id = %s", [id_room])
    return json.dumps({"info": "status='started'"})


@app.route('/closeRoom')
def close_room():
    id_room = request.args.get('id')
    db.exec_query("UPDATE Room  r SET r.status='closed' WHERE r.id = %s", [id_room])
    return json.dumps({"info": "status='closed'"})


@app.route('/finishRoom')
def finish_room():
    id_room = request.args.get('id')
    db.exec_query("UPDATE Room  r SET r.status='finished' WHERE r.id = %s", [id_room])
    ranking = []
    # for
    # SELECT id, COUNT(a.id), COUNT(a.id) FROM Room r INNER JOIN
    values = db.exec_query("SELECT qq.askedUserId, COUNT(qq.id) "
                           "FROM QuizQuestion qq "
                           "WHERE qq.correctanswerId = qq.answeredId "
                           "GROUP BY qq.id", [])
    # SELECT qq.askedUserId, COUNT(qq.id) FROM quizquestion qq WHERE qq.correctanswerId = qq.answeredId
    return json.dumps({
        [{"email": "hola@iñi", "correct": 23}]
    })


@app.route('/statusRoom')
def status_room():
    id_room = request.args.get('id')
    # SELECT status FROM Room WHERE id = 1
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
        return json.dumps({"error": "no JSON found"})
    else:
        user_id = json_data["idUser"]
        values = []
        for a in json_data["answers"]:
            values.append((a["id"], user_id, a["text"]))
            print(values[len(values) - 1])
        db.exec_many_query("INSERT INTO Answer (questionId, userId, answer) VALUES(%s,%s,%s)", values)
        return json.dumps({"info": "Data received"})


@app.route('/getQuizQuestion')
def get_question():
    idRoom = int(request.args.get('idRoom'))
    idUser = int(request.args.get('idUser'))
    
    possibleQuestions = db.getNonAnsweredQuestions(idRoom,idUser)
    possibleUsersToAsk = db.getNonAnsweredPeople(idRoom,idUser)
    
    questionId = []
    askedAboutId = []
    
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

    if len(questionId) > 0 and 0 < len(askedAboutId):
        quizQuestionId = db.insertQuizQuestion(idUser,askedAboutId[0],questionId[0])

        otherUsers = db.getAllDifferentPeople(idRoom,askedAboutId[0])
        
        random.shuffle(otherUsers)
        
        
        answers = []
        (answerId,textId) = db.getAnswer(questionId[0],askedAboutId[0])

        db.exec_query("UPDATE QuizQuestion SET correctanswerId=%s WHERE id = %s", [answerId, quizQuestionId])

        answers.append((answerId,textId))
        if min(numberOfAnswers-1 , len(otherUsers)) > 0:
            for i in range( min(numberOfAnswers-1 , len(otherUsers) )):
                (answerId,textId) = db.getAnswer(questionId[0],otherUsers[i])
                answers.append((answerId,textId))
        
        #if commented the first answer will be the correct one
        random.shuffle(answers)
        
        
        answerJson = []
        for (answerId,textId) in answers:
            answerJson.append({"id": answerId ,"text":textId})

        print (quizQuestionId);
        #SELECT 'question' FROM 'Question' WHERE 'id' = 3
        value = db.exec_query("SELECT id "
                              "FROM QuizQuestion "
                              "WHERE askedUserId=%s AND aboutUserId=%s AND questionId=%s",
                              [idUser, askedAboutId[0], questionId[0]])
        quizQuestionId = value[0][0]

        value = db.exec_query("SELECT q.question "
                              "FROM Question q "
                              "WHERE q.id = %s",
                              [questionId[0]])

        question_text = value[0][0]

        value = db.exec_query("SELECT u.email "
                              "FROM Users u "
                              "WHERE u.id=%s",
                              [askedAboutId[0]])
        user_name = value[0][0]

        question_text = "What did " + user_name + " answer about " + question_text + " ?"
        
        return json.dumps({
              "id": quizQuestionId,
              "question": question_text,
              "answers": answerJson
            })
    else:
        return json.dumps({"error": "Not available questions for this user in this room"})


@app.route('/postAnswer')
def post_answer():
    quizQuestionId = request.args.get('quizQuestionId')
    answerId = request.args.get('answerId')

    db.exec_query("UPDATE QuizQuestion SET answeredId = %s WHERE id = %s", [answerId, quizQuestionId])


    value = db.exec_query("SELECT qq.answeredId , qq.correctanswerId, qq.questionId  FROM QuizQuestion qq WHERE qq.id = %s", [quizQuestionId])

    answeredId = value[0][0]
    correctanswerId = value[0][1]
    questionId = value[0][2]

    value = db.exec_query("SELECT a.answer FROM Answer a WHERE a.id = %s ", [correctanswerId] )

    if len(value) > 0:
        text = value[0][0]
    else :
        text = "something when wrong"

    #update UPDATE quizquestion SET answeredId=5 WHERE id = 1

    if value is None:
        return json.dumps({"error": "Internal server error"})
    return json.dumps({
          "correct": answeredId == correctanswerId,
          "question": questionId,
          "correctAnswer": {"id": correctanswerId, "text": text}
        })

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', threaded=True)
