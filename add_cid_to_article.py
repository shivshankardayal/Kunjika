from couchbase import Couchbase
import urllib2
import json

kb = Couchbase.connect("kunjika")

articles = urllib2.urlopen('http://localhost:8092/kunjika/_design/dev_qa/_view/get_articles?reduce=false').read()
articles = json.loads(articles)['rows']

for row in articles:
    article = kb.get(row['id']).value
    if 'cids' not in article:
        article['cids'] = []
        kb.replace(row['id'], article)