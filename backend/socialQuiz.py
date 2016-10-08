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
	return json.dumps({ "id" : 12345678 })


if __name__ == '__main__':
	app.run(debug=True, host='127.0.0.1')