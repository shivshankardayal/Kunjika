# script to convert entire markdown content to html

from couchbase import Couchbase
import markdown
import bleach
import urllib2
import kunjika
import json

cb = Couchbase.connect("default")
qb = Couchbase.connect("questions")
tb = Couchbase.connect("tags")
kb = Couchbase.connect("kunjika")

DB_URL = 'http://localhost:8092/'

ucount = cb.get('count').value
qcount = qb.get('qcount').value
tcount = tb.get('tcount').value

for i in xrange(1, ucount+1):
    user = cb.get(str(i)).value
    if 'about-me' in user:
        user['about-me-html'] = bleach.clean(markdown.markdown(user['about-me'], extensions=['extra', 'codehilite', 'oembed'],
                                                               output_format='html5'), kunjika.tags_wl, kunjika.attrs_wl)
        cb.set(str(i), user)

doc = urllib2.urlopen(DB_URL + 'tags/_design/dev_qa/_view/get_tag_by_id').read()
doc = json.loads(doc)

for row in doc['rows']:
    tag = tb.get(row['id']).value
    tag['info-html'] = bleach.clean(markdown.markdown(tag['info'], extensions=['extra', 'codehilite', 'oembed'],
                                                      output_format='html5'), kunjika.tags_wl, kunjika.attrs_wl)

    tb.set(row['id'], tag)

for i in xrange(1, qcount+1):
    q = qb.get(str(i)).value
    q['content']['html'] = bleach.clean(markdown.markdown(q['content']['description'], extensions=['extra', 'codehilite', 'oembed'],
                                                          output_format='html5'), kunjika.tags_wl, kunjika.attrs_wl)
    if 'answers' in q:
        for answer in q['answers']:
            answer['html'] = bleach.clean(markdown.markdown(answer['answer'], extensions=['extra', 'codehilite', 'oembed'],
                                                            output_format='html5'), kunjika.tags_wl, kunjika.attrs_wl)
            if 'comments' in answer:
                for comment in answer['comments']:
                    comment['html'] = bleach.clean(markdown.markdown(comment['comment'], extensions=['extra', 'codehilite', 'oembed'],
                                                                     output_format='html5'), kunjika.tags_wl, kunjika.attrs_wl)

    if 'comments' in q:
        for comment in q['comments']:
            comment['html'] = bleach.clean(markdown.markdown(comment['comment'], extensions=['extra', 'codehilite', 'oembed'],
                                                             output_format='html5'), kunjika.tags_wl, kunjika.attrs_wl)

    qb.set(str(i), q)

doc = urllib2.urlopen(DB_URL + 'kunjika/_design/dev_qa/_view/get_articles?reduce=false').read()
doc = json.loads(doc)

for row in doc['rows']:
    article = kb.get(row['id']).value
    article['html'] = bleach.clean(markdown.markdown(article['content'], extensions=['extra', 'codehilite', 'oembed'],
                                                     output_format='html5'), kunjika.tags_wl, kunjika.attrs_wl)

    if 'cids' in article:
        for cid in article['cids']:
            comment = kb.get(cid).value
            comment['html'] = bleach.clean(markdown.markdown(comment['comment'], extensions=['extra', 'codehilite', 'oembed'],
                                                             output_format='html5'), kunjika.tags_wl, kunjika.attrs_wl)
            kb.set(cid, comment)
    kb.set(row['id'], article)
