#!/bin/bash
. venv/bin/activate

python3 social_quiz.py -t > log.txt 2> err.txt &
