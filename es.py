from kunjika import conn
import pyes

def index(title, url, body, qid):

    try:
        conn.delete_index_if_exists('kunjika')
        conn.create_index('kunjika')
    except:
        pass

    kunjika = {
        u'title':{'boost': 1.0,
        'index': 'analyzed',
        'store': 'yes',
        'type': u'string',},
        u'body':{'boost': 1.0,
        'index': 'analyzed',
        'store': 'yes',
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
        conn.delete_mapping('kunjika', {'properties': kunjika})
        conn.put_mapping('kunjika', {'properties': kunjika}, ['kunjika'])
    except:
        print "Already exists"

    conn.index({'title': title, 'body': body, 'url': url, 'qid': qid}, 'kunjika', 'kunjika', qid)

    conn.refresh()

def search(query):

    q = pyes.TextQuery('title', query)
    return conn.search(query=q)
