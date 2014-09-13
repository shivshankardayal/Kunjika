from couchbase import Couchbase
import urllib2
import json
tb = Couchbase.connect("tags")

doc = urllib2.urlopen('http://localhost:8092/tags/_design/dev_qa/_view/get_tag_by_id').read()

doc = json.loads(doc)

print len(doc['rows'])
tb.set('tcount', len(doc['rows']))

i = 0
for row in doc['rows']:
    i += 1
    tag = tb.get(row['id']).value
    tag['tid'] = i
    print tag
    tb.set(row['id'], tag)
