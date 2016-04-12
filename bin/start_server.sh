#! /bin/bash

echo "-> Install requirements"
pip install -r requirements.txt

echo "-> Starting server"
lektor server -p 8000 -h 0.0.0.0
