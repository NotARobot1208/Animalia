#!/bin/bash

python3 /app/webapp/app.py &
python3 /app/websocketapp/main.py &
python3 /app/chatapp/main.py
cat
