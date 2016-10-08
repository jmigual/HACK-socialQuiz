#!/bin/bash
. venv/bin/activavte
python3 -m flask run -host=0.0.0.0 > log.txt 2> err.txt &
