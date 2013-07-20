# Copyright (c) 2013 Shiv Shankar Dayal
# This file is part of Kunjika.
#
# Kunjika is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# Kunjika is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
import kunjika
from flask import jsonify, g
from math import ceil
import urllib2
import json
from time import strftime, localtime
from flask import url_for, request

def generate_url(title):
    length = len(title)
    prev_dash = False
    url = ""
    for i in range(length):
        c = title[i]
        if (c >= 'a' and c <= 'z') or (c >= '0' and c <= '9'):
            url += c
            prev_dash = False
        elif c >= 'A' and c <= 'Z':
            url += c
        elif c == ' ' or c == ',' or c == '.' or c == '/' or c == '\\' or c == '-' or c == '_' or c == '=':
            if not prev_dash and len(url) > 0:
                url += '-'
                prev_dash = True
        elif ord(c) > 160:
            c = c.decode('UTF-8').lower()
            url += c
            prev_dash = False
        if i == 80:
            break

    if prev_dash is True:
        url = url[:-1]

    return url


def accept_answer(idntfr):

    idntfr = idntfr[4:]

    idntfr_list = idntfr.split('-')
    qid = idntfr_list[0]
    aid = idntfr_list[1]

    question = kunjika.qb.get(qid).value

    voter = kunjika.cb.get(str(g.user.id)).value

    if int(question['content']['op']) != g.user.id:
        return jsonify({"success": False})
    for answer in question['answers']:
        if answer['aid'] != int(aid):
            if answer['best'] == True:
                receiver = kunjika.cb.get(str(answer['poster'])).value
                receiver['rep'] -= 10
                voter['rep'] -= 2
                kunjika.cb.replace(str(answer['poster']), receiver)
                kunjika.cb.replace(str(voter['id']), voter)
                answer['best'] = False

        else:
            if answer['best'] != True:
                answer['best'] = True
                receiver = kunjika.cb.get(str(answer['poster'])).value
                receiver['rep'] += 10
                voter['rep'] += 2
                kunjika.cb.replace(str(answer['poster']), receiver)
                kunjika.cb.replace(str(voter['id']), voter)
            else:
                receiver = kunjika.cb.get(str(answer['poster'])).value
                receiver['rep'] -= 10
                voter['rep'] -= 2
                kunjika.cb.replace(str(answer['poster']), receiver)
                kunjika.cb.replace(str(voter['id']), voter)
                answer['best'] = False


    kunjika.qb.replace(qid, question)

    return jsonify({"success": True})

def handle_favorite(idntfr):

    qid = idntfr[3:]

    #print qid
    question = kunjika.qb.get(qid).value
    #user = kunjika.cb.get(str(g.user.id)).value

    #print question
    #print user
    if 'users_fav' in question:
        if g.user.id in question['users_fav']:
            question['users_fav'].remove(g.user.id)
        else:
            question['users_fav'].append(g.user.id)
    else:
        question['users_fav'] = []
        question['users_fav'].append(g.user.id)

    # Issue #9
    #if 'fav_q' in user:
    #    if qid in user['fav_q']:
    #       user['fav_q'].remove(qid)
    #    else:
    #        user['fav_q'].append(qid)
    #else:
    #    user['fav_q'] = []
    #    user['fav_q'].append(qid)

    #kunjika.cb.replace(str(g.user.id), user)
    kunjika.qb.replace(qid, question)

    return jsonify({"success": True})


class Pagination(object):

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
                (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
                num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

def get_questions_for_page(page, QUESTIONS_PER_PAGE, count):

    skip = (page - 1) * QUESTIONS_PER_PAGE
    questions = urllib2.urlopen(
                kunjika.DB_URL + 'questions/_design/dev_qa/_view/get_questions?limit=' +
                str(QUESTIONS_PER_PAGE) + '&skip=' + str(skip) + '&descending=true').read()

    questions = json.loads(questions)
    ##print questions
    question_list = []
    for i in questions['rows']:
        question_list.append(i['value'])

    for i in question_list:
        i['tstamp'] = strftime("%a, %d %b %Y %H:%M", localtime(i['content']['ts']))

        user = kunjika.cb.get(i['content']['op']).value
        i['opname'] = user['name']

    return question_list

def get_tags_per_page(page, TAGS_PER_PAGE, count):

    skip = (page - 1) * TAGS_PER_PAGE
    tags = urllib2.urlopen(
                kunjika.DB_URL + 'tags/_design/dev_qa/_view/get_by_count?limit=' +
                str(TAGS_PER_PAGE) + '&skip=' + str(skip) + '&descending=true').read()
    tags = json.loads(tags)

    tags_list = []

    for i in tags['rows']:
        tags_list.append(i['value'])

    return tags_list

def get_users_per_page(page, USERS_PER_PAGE, count):

    skip = (page - 1) * USERS_PER_PAGE
    users = urllib2.urlopen(
                kunjika.DB_URL + 'default/_design/dev_qa/_view/get_by_reputation?limit=' +
                str(USERS_PER_PAGE) + '&skip=' + str(skip) + '&descending=true').read()
    users = json.loads(users)

    users_list = []

    for i in users['rows']:
        users_list.append(i['value'])

    return users_list

def get_questions_for_tag(page, QUESTIONS_PER_PAGE, tag):

    skip = (page - 1) * QUESTIONS_PER_PAGE
    tag = urllib2.quote(tag, '')
    tag = urllib2.urlopen(kunjika.DB_URL + 'tags/_design/dev_qa/_view/get_doc_from_tag?&key=' + '"' + tag + '"').read()
    tag = json.loads(tag)['rows'][0]['value']
    question_list = []
    for qid in tag['qid']:
        question_list.append(kunjika.qb.get(str(qid)).value)

    for i in question_list:
        i['tstamp'] = strftime("%a, %d %b %Y %H:%M", localtime(i['content']['ts']))

        user = kunjika.cb.get(i['content']['op']).value
        i['opname'] = user['name']

    return question_list

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)

def url_for_other_user_question_page(page):
    args = request.view_args.copy()
    args['qpage'] = page
    return url_for(request.endpoint, **args)

def url_for_other_user_answer_page(page):
    args = request.view_args.copy()
    args['apage'] = page
    return url_for(request.endpoint, **args)


def get_popular_tags():

    tag_list = urllib2.urlopen(kunjika.DB_URL + 'tags/_design/dev_qa/_view/get_by_count?descending=true').read()
    tag_list = json.loads(tag_list)['rows']

    tags = []
    for i in tag_list:
        tags.append(i['value'])

    return tags

def filter_by(email):

    user = urllib2.urlopen(
                kunjika.DB_URL + 'default/_design/dev_qa/_view/get_id_from_email?key=' + '"' + email + '"').read()
    user = json.loads(user)
    if len(user['rows']) == 1:
        user = user['rows'][0]['value']
        return user
    else:
        return None


def get_user_questions_per_page(user, qpage, USER_QUESTIONS_PER_PAGE, qcount):
    # Issue 9

    #if 'questions' in user:
    #    qid_list = user['questions'][(qpage - 1)*USER_QUESTIONS_PER_PAGE:qpage*USER_QUESTIONS_PER_PAGE]
    #else:
    #    return None

    skip = (qpage - 1) * USER_QUESTIONS_PER_PAGE
    question_list = []
    question_view = urllib2.urlopen(
        kunjika.DB_URL + 'questions/_design/dev_qa/_view/get_questions_by_userid?key=' + '"' +str(user['id'])
        + '"' + '&desending=true&skip=' + str(skip) + '&limit=' + str(USER_QUESTIONS_PER_PAGE)
    ).read()
    question_view = json.loads(question_view)
    for element in question_view['rows']:
        question_list.append(element['value'])

    #for qid in qid_list:
    #    question = kunjika.qb.get(str(qid)).value
    #    question_list.append(question)

    return question_list

def get_user_answers_per_page(user, apage, USER_ANSWERS_PER_PAGE, acount):
    #the following is aid in the form of 'qid-aid'
    # Issue 9
    #if 'answers' in user:
    #    aid_list = user['answers'][(apage - 1)*USER_ANSWERS_PER_PAGE:apage*USER_ANSWERS_PER_PAGE]
    #else:
    #    return None

    skip = (apage - 1)*USER_ANSWERS_PER_PAGE
    question_list = []
    question_view = urllib2.urlopen(
        kunjika.DB_URL + 'questions/_design/dev_qa/_view/get_answers_by_userid?key=' +str(user['id'])
        + '&desending=true&skip=' + str(skip) + '&limit=' + str(USER_ANSWERS_PER_PAGE)
    ).read()
    question_view = json.loads(question_view)
    for element in question_view['rows']:
        question_list.append(element['value'])
    aids = []
    for question in question_list:
        for answer in question['answers']:
            aids.append(answer['aid'])
    #let us get question ids and questions
    #for aid in aid_list:
    #    qid = aid.split('-')[0]
    #    single_aid = aid.split('-')[1]
    #    #print qid
    #    #print single_aid
    #    question = kunjika.qb.get(qid).value
    #    question_list.append(question)
    #    aids.append(single_aid)

    return question_list, aids
