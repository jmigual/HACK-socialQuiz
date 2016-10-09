#!/bin/bash
. venv/bin/activate

export FLASK_APP=socialQuiz.py

python3 $FLASK_APP > log.txt 2> err.txt &
