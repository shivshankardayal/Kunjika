#!/bin/bash

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

virtualenv venv
source venv/bin/activate
pip install --upgrade Flask Flask-WTF Flask-Bcrypt Flask-Gravatar Flask-Login couchbase itsdangerous Flask-mail Flask-OpenID \
Flask-Classy pyes 
