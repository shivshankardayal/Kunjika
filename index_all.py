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

# We index all the questions, tags and users to elasticsearch using this
# script.

import pyes
from couchbase.views.iterator import View, Query
from couchbase import Couchbase
from couchbase.exceptions import *
import urllib2
import json

cb = Couchbase.connect("default")
qb = Couchbase.connect("questions")
tb = Couchbase.connect("tags")
pb = Couchbase.connect("polls")
es_conn = pyes.ES('http://localhost:9200/')

questions_mapping = {
     'title': {
         'boost': 1.0,
         'index': 'analyzed',
         'store': 'yes',
         'type': 'string',
         "term_vector": "with_positions_offsets"
     },
     'description': {
         'boost': 1.0,
         'index': 'analyzed',
         'store': 'yes',
         'type': 'string',
         "term_vector": "with_positions_offsets"
     },
     'qid': {
         'boost': 1.0,
         'index': 'not_analyzed',
         'store': 'yes',
         'type': 'integer',
         "term_vector": "with_positions_offsets"
     }
}

users_mapping = {
     'name': {
         'boost': 1.0,
         'index': 'analyzed',
         'store': 'yes',
         'type': 'string',
         "term_vector": "with_positions_offsets"
     },
     'uid': {
         'boost': 1.0,
         'index': 'not_analyzed',
         'store': 'yes',
         'type': 'integer',
         "term_vector": "with_positions_offsets"
     }
}

tags_mapping = {
     'tag': {
         'boost': 1.0,
         'index': 'analyzed',
         'store': 'yes',
         'type': 'string',
         "term_vector": "with_positions_offsets"
     },
     'tid': {
         'boost': 1.0,
         'index': 'not_analyzed',
         'store': 'yes',
         'type': 'integer',
         "term_vector": "with_positions_offsets"
     }
}

# Initialize indices for different buckets
try:
    #es_conn.indices.delete_index("questions")
    es_conn.indices.create_index("questions")
except:
    pass

try:
    #es_conn.indices.delete_index("users")
    es_conn.indices.create_index("users")
except:
    pass

try:
    #es_conn.indices.delete_index("tags")
    es_conn.indices.create_index("tags")
except:
    pass

es_conn.indices.put_mapping("questions-type", {'properties':questions_mapping}, ["questions"])
es_conn.indices.put_mapping("users-type", {'properties':users_mapping}, ["users"])
es_conn.indices.put_mapping("tags-type", {'properties':tags_mapping}, ["tags"])

questions = urllib2.urlopen("http://localhost:8092/questions/_design/dev_qa/_view/get_questions?descending=true&stale=false").read()
questions = json.loads(questions)
##print questions
question_list = []
for i in questions['rows']:
    question_list.append(str(i['id']))

val_res = qb.get_multi(question_list)
questions = []
for qid in question_list:
	questions.append(val_res[str(qid)].value)
for question in questions:
    #print question
    es_conn.index({'title':question['title'], 'description':question['content']['description'], 'qid':int(question['qid']),
                   'position':int(question['qid'])}, 'questions', 'questions-type', int(question['qid']))

es_conn.indices.refresh('questions')

rows = urllib2.urlopen('http://localhost:8092/tags/_design/dev_qa/_view/get_tag_by_id').read()
rows = json.loads(rows)['rows']
tids_list = []
for row in rows:
    tids_list.append(str(row['id']))

if len(tids_list) != 0:
    val_res = tb.get_multi(tids_list)

tags = []

for tid in tids_list:
    tags.append(val_res[str(tid)].value)

for tag in tags:
    es_conn.index({'tag':tag['tag'], 'tid':tag['tid'], 'position':tag['tid']}, 'tags', 'tags-type', tag['tid'])

es_conn.indices.refresh('tags')

rows = urllib2.urlopen('http://localhost:8092/default/_design/dev_qa/_view/get_by_reputation').read()
rows = json.loads(rows)['rows']
uids_list = []
for row in rows:
    uids_list.append(str(row['id']))

if len(uids_list) != 0:
    val_res = cb.get_multi(uids_list)

users = []

for uid in uids_list:
    users.append(val_res[str(uid)].value)

for user in users:
    es_conn.index({'name':user['name'], 'uid':user['id'], 'position':user['id']}, 'users', 'users-type', user['id'])
es_conn.indices.refresh('users')
