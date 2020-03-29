#!/bin/bash

cd DATABASE_ENV
pwd

source env/bin/activate

pip install -r ../requirements.txt
cd ../DATABASE_ENGINE
python3 main.py &