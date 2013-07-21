import pyes
import urllib2
import json
from kunjika import DB_URL

conn = pyes.ES('127.0.0.1:9200')

try:
    conn.delete_index_if_exists('kunjika')
    conn.create_index('kunjika')
except:
    pass

kunjika = {
    u'title':{'boost': 10.0,
    'index': 'analyzed',
    'store': 'yes',
    'type': u'string',
    'term_vector': 'with_positions_offsets'},
    u'body':{'boost': 5.0,
    'index': 'analyzed',
    'store': 'no',
    'type': u'string',
    'term_vector': 'with_positions_offsets'},
    u'url':{'boost': 1.0,
    'index': 'not_analyzed',
    'store': 'yes',
    'type': u'string',
    'term_vector': 'with_positions_offsets'},
    u'qid':{'boost': 1.0,
    'index': 'not_analyzed',
    'store': 'yes',
    'type': u'integer',
    'term_vector': 'with_positions_offsets'},
        }


try:
    conn.put_mapping('kunjika', {'properties': kunjika}, ['kunjika'])
except:
    pass

questions = urllib2.urlopen(
    DB_URL + 'questions/_design/dev_qa/_view/get_questions'
).read()

questions = json.loads(questions)

for question in questions['rows']:
    conn.index({'title': question['value']['title'], 'body': question['value']['content']['description'], \
                'url': question['value']['content']['url'], \
                'qid': question['value']['qid']}, 'kunjika', 'kunjika', question['value']['qid'])

conn.refresh()
