#!/bin/bash

cd DATABASE_ENV
pwd

source env/bin/activate

cd ../DATABASE_ENGINE
pip install -r requirements.txt

python3 main.py &
xdg-open http://localhost:8080