#!/bin/bash

virtualenv venv
source venv/bin/activate
pip install --upgrade Flask Flask-WTF Flask-Bcrypt Flask-Gravatar Flask-Login couchbase itsdangerous Flask-mail
