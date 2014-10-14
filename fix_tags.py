import pyes
from couchbase import Couchbase
import urllib2
import json
tb = Couchbase.connect("tags")

doc = urllib2.urlopen('http://localhost:8092/tags/_design/dev_qa/_view/get_tag_by_id').read()

doc = json.loads(doc)

count = len(doc['rows'])

i = 0
for row in doc['rows']:
    i += 1
    tag = tb.get(row['id']).value
    tag['tid'] = i
    print tag
    tb.set(row['id'], tag)
    if tag['count'] == 0:
        tb.delete(row['id'])
        count = count -1

print len(doc['rows'])
tb.set('tcount', len(doc['rows']))

es_conn = pyes.ES('http://localhost:9200/')

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
    es_conn.indices.delete_index("questions")
    es_conn.indices.create_index("tags")
except:
    pass

es_conn.indices.put_mapping("tags-type", {'properties':tags_mapping}, ["tags"])
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
