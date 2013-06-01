from kunjika import kunjika, qc, qb, cb
import urllib2
import json
from time import localtime, strftime

def get_question_by_id(qid, question):
    print qid
    question = qb.get(qid)[2]
    question = json.loads(question)
    print question

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
        i['content']['tags'] = i['content']['tags'].split(',')
        print i
        uid = i['content']['op']
        try:
            user = cb.get(uid)[2]
        except:
            print "Exception caught"
        user = json.loads(user)
        i['fname'] = user['fname']
        i['ts'] = strftime("%a, %d %b %Y %H:%M:%S", localtime(i['content']['ts']))

    return question_list

