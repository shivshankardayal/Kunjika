from kunjika import kunjika, qb, cb
import urllib2
import json
from time import localtime, strftime
from flaskext.gravatar import Gravatar

def get_question_by_id(qid, question):
    question = qb.get(qid).value

    question['tstamp'] = strftime("%a, %d %b %Y %H:%M:%S", localtime(question['content']['ts']))
    user = cb.get(question['content']['op']).value
    question['email'] = user['email']
    question['opname'] = user['fname']

    if'comments' in question:
        for i in question['comments']:
            i['tstamp'] = strftime("%a, %d %b %Y %H:%M:%S", localtime(i['ts']))
    if 'answers' in question:
        for i in question['answers']:
            user = cb.get(str(i['poster'])).value
            #user = json.loads(user)
            i['opname'] = user['fname']
            i['email'] = user['email']
            i['tstamp'] = strftime("%a, %d %b %Y %H:%M", localtime(i['ts']))
            if 'comments' in i:
                for i in i['comments']:
                    i['tstamp'] = strftime("%a, %d %b %Y %H:%M", localtime(i['ts']))

    return question

def get_questions():
    questions = urllib2.urlopen("http://localhost:8092/questions/_design/dev_dev/_view/get_questions?descending=true&limit=20").read()
    questions = json.loads(questions)
    print questions
    question_list = []
    for i in questions['rows']:
        question_list.append(i['value'])

    for i in question_list:
        i['tstamp'] = strftime("%a, %d %b %Y %H:%M", localtime(i['content']['ts']))

        user = cb.get(i['content']['op']).value
        i['opname'] = user['fname']

    return question_list

