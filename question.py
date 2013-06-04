from kunjika import kunjika, qb, cb
import urllib2
import json
from time import localtime, strftime
from flaskext.gravatar import Gravatar

def get_question_by_id(qid, question):
    #print qid
    question = qb.get(qid)[2]
    question = json.loads(question)
    #print question

    question['tstamp'] = strftime("%a, %d %b %Y %H:%M:%S", localtime(question['content']['ts']))
    user = cb.get(question['content']['op'])[2]
    user = json.loads(user)
    question['email'] = user['email']
    question['opname'] = user['fname']

    if 'answers' in question:
        for i in question['answers']:
            user = cb.get(str(i['poster']))[2]
            user = json.loads(user)
            i['opname'] = user['fname']
            i['email'] = user['email']
            i['tstamp'] = strftime("%a, %d %b %Y %H:%M:%S", localtime(i['ts']))

    return question

def get_questions():
    questions = urllib2.urlopen("http://localhost:8092/questions/_design/dev_dev/_view/get_questions?descending=true&limit=20").read()
    #print "1"
    questions = json.loads(questions)
    question_list = []
    for i in questions['rows']:
        question_list.append(i['value'])

    #print "2"
    for i in question_list:
        #print i
        i['tstamp'] = strftime("%a, %d %b %Y %H:%M", localtime(i['content']['ts']))

        user = cb.get(i['content']['op'])[2]
        user = json.loads(user)
        i['opname'] = user['fname']

    return question_list

