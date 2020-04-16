#!/bin/bash

cd DATABASE_ENV
pwd

source env/bin/activate

pip install -r ../DATABASE_ENGINE/requirements.txt

cd ../DATABASE_ENGINE
pwd

python3 main.py &
xdg-open http://localhost:8080
