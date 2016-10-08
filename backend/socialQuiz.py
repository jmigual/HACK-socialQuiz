# -*- coding: utf-8 -*-

from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/')
def index():
	return "Hello world"

@app.route('/register/<string:mail>')
def register(mail):
	return "Your mail is: " + mail + " " + request.args.get('mail')


if __name__ == '__main__':
	app.run(debug=True, host='127.0.0.1')