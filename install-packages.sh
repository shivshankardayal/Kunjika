#!/bin/bash

virtualenv venv
source venv/bin/activate
pip install Flask Flask-WTF Flask-Bcrypt Flask-Gravatar Flask-Login couchbase
