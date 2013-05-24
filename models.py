from kunjika import kunjika
from mongoengine import *
import datetime

connect('kunjika', host=kunjika.config['DB_HOST'], port=kunjika.config['DB_PORT'])

class Comments(Document):
    comment = StringField(required=True, max_length=kunjika.config['MAX_COMMENT_LENGTH'],
                          min_length=kunjika.config['MIN_COMMENT_LENGTH'])
    commentator =