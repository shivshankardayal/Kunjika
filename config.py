# Copyright (c) 2013 Shiv Shankar Dayal
# This file is part of Kunjika.
#
# Kunjika is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# Kunjika is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.

# CSRF section
# Keep keys complex and never share. You must edit these.
CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
CSRF_SESSION_KEY="somethingimpossibletoguess"

# OpenID section
# This is not used as of now.
OPENID_PROVIDERS = [
    { 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id' },
    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
    { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
    { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
    { 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' }]

# Database section. You must edit these.

DB_HOST = 'localhost'
DB_PORT = '8091'

# reCaptcha seaction
# Your google recaptcha keys. You must edit these.
RECAPTCHA_USE_SSL = False
RECAPTCHA_PUBLIC_KEY = '6Lc-t-ASAAAAAB0YkGtdwfWS4lJio8-aCf4IM1II'
RECAPTCHA_PRIVATE_KEY = '6Lc-t-ASAAAAABjbkjOyZpnD1wZ4VEstwQUtQ3Pb'
RECAPTCHA_OPTIONS = {'theme': 'white'}

# google analytics key. You must edit these.
GOOGLE_ANALYTICS_KEY = 'jhegsbkgkw'

# Application configuration section

#  Tune as per requirement

MAX_COMMENT_LENGTH = 400
MIN_COMMENT_LENGTH = 20

QUESTIONS_PER_PAGE = 50
TAGS_PER_PAGE = 40
USERS_PER_PAGE = 40
USER_QUESTIONS_PER_PAGE = 10
USER_ANSWERS_PER_PAGE = 10

# You must edit these.
ADMIN_EMAIL='shivshankar.dayal@gmail.com'

# set RESET_PASSWORD to something difficult. Do not worry it is like
# a bcrypt hash. But do not share

MAX_FAILED_LOGINS = 10

# You must edit these.
RESET_PASSWORD = "some bad password"

QUESTIONS_PER_MIN = 2
QUESTIONS_PER_HR = 10
QUESTIONS_PER_DAY = 20

ANSWERS_PER_MIN = 5
ANSWERS_PER_HR = 20
ANSWERS_PER_DAY = 50

COMMENTS_PER_MIN = 5
COMMENTS_PER_HR = 20
COMMENTS_PER_DAY = 50

#  You database URL, DNS and mail server IP. You must edit these.
DB_URL = 'http://localhost:8092/'
HOST_URL = 'http://localhost:5000/'
MAIL_SERVER_IP = '127.0.0.1'
ES_URL = '127.0.0.1'
DEBUG_MODE = True

# log file path. You must edit these.
LOG_FILE = '/var/www/Kunjika/kunjika.log'

#  log file size
MAX_LOG_SIZE = 10 * 1024 *1024

# backup of logs will not be deleted for 0 count
BACKUP_COUNT = 0

# upload folder. You must edit these.
UPLOAD_FOLDER = '/var/www/Kunjika/uploads'

#  upload size. tune as you need
MAX_CONTENT_LENGTH = 2 * 1024 * 1024
