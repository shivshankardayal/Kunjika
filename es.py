import pyes

conn = pyes.ES('127.0.0.1:9200')
conn.create_index("kunjika")

mapping = {u'title':{'boost': 1.0,
    'index': 'analyzed',
    'store': 'yes',
    'term_vector': 'with_positions_offsets'},
    u'url':{'boost': 1.0,
    'index': 'analyzed',
    'store': 'yes',
    'term_vector': 'with_positions_offsets'},
        }

conn.put_mapping('kunjika', {'properties': mapping}, ['kunjika'])
