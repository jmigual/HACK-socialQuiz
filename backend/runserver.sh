#!/bin/bash
. venv/bin/activate

export FLASK_APP=socialQuiz.py

python3 -m flask run --host=0.0.0.0 > log.txt 2> err.txt &
