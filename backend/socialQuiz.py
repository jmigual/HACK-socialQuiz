# -*- coding: utf-8 -*-

from flask import Flask
from flask import request
import json

app = Flask(__name__)


@app.route('/')
def index():
    return "Hello world"


@app.route('/register/')
def register():
    # To obtain the mail
    email = request.args.get('email')
    return json.dumps({"id": 12345678})


@app.route('/joinRoom')
def join_room():
    idRoom = request.args.get('idRoom')
    email = request.args.get('email')
    return json.dumps({"id": 12345678})


@app.route('/getUserId')
def get_user_id():
    email = request.args.get('email')
    return json.dumps({"id": 12345678})


@app.route('/createRoom')
def create_room():
    id = request.args.get('id')
    return json.dumps({"id": 123 })


@app.route('/fillRoom')
def fill_room():
    print(request.form())


@app.route('/getRoomQuestion')
def get_room_question():
    idRoom = request.args.get('idRoom')
    return json.dumps({"questions": [
        {"id": 2113, "text": "How do you feel?"},
        {"id": 2114, "text": "Do you want a kiss?"}]})


@app.route('/postRoomAnswers')
def post_room_answers():
    print(request.form())



if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
