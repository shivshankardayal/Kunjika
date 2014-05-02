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

import kunjika
import urllib2
import json
from time import localtime, strftime
from flaskext.gravatar import Gravatar

def get_question_by_id(qid, question):
    question = kunjika.qb.get(qid).value

    question['tstamp'] = strftime("%a, %d %b %Y %H:%M", localtime(question['content']['ts']))
    user = kunjika.cb.get(question['content']['op']).value
    question['email'] = user['email']
    question['opname'] = user['name']

    if'comments' in question:
        for i in question['comments']:
            i['tstamp'] = strftime("%a, %d %b %Y %H:%M:%S", localtime(i['ts']))
    if 'answers' in question:
        for i in question['answers']:
            user = kunjika.cb.get(str(i['poster'])).value
            #user = json.loads(user)
            i['opname'] = user['name']
            i['email'] = user['email']
            i['tstamp'] = strftime("%a, %d %b %Y %H:%M", localtime(i['ts']))
            if 'comments' in i:
                for i in i['comments']:
                    i['tstamp'] = strftime("%a, %d %b %Y %H:%M", localtime(i['ts']))

    return question

def get_questions():
    questions = urllib2.urlopen(kunjika.DB_URL + "/_design/dev_qa/_view/get_questions?stale=false").read()
    questions = json.loads(questions)
    ##print questions
    question_list = []
    for i in questions['rows']:
        question_list.append(i['value'])

    for i in question_list:
        i['tstamp'] = strftime("%a, %d %b %Y %H:%M", localtime(i['content']['ts']))

        user = kunjika.cb.get(i['content']['op']).value
        i['opname'] = user['name']

    return question_list

