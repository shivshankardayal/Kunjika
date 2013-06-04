#!/bin/bash

virtualenv-2.7 venv
source venv/bin/activate
pip install Flask Flask-WTF Flask-Bcrypt Flask-Gravatar Flask-Login couchbase
