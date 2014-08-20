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

from flask import (Flask, session, render_template, abort, redirect, url_for, flash,
                   make_response, request, g, jsonify)
import json
from forms import *
from flask.ext.bcrypt import Bcrypt
from couchbase import Couchbase
from couchbase.exceptions import *
import urllib2
from flaskext.gravatar import Gravatar
from werkzeug import secure_filename, SharedDataMiddleware
import os
from os.path import basename
from time import localtime, strftime, time, mktime
from datetime import datetime
from flask.ext.login import (LoginManager, current_user, login_required, login_user,
                             logout_user, UserMixin, AnonymousUserMixin, confirm_login,
                             fresh_login_required)
from models import User, Anonymous
import question
import votes
import edit
import utility
import jinja2
from flask.ext.mail import Mail, Message
from urlparse import urljoin
from werkzeug.contrib.atom import AtomFeed
from flask_openid import OpenID
from itsdangerous import TimestampSigner
from flask_wtf import Form, RecaptchaField
from wtforms import (BooleanField, TextField, PasswordField, validators, TextAreaField, RadioField, SelectField,
                     HiddenField)
import pyes
import urllib
from couchbase.views.iterator import View, Query
from uuid import uuid1
from threading import Thread
import base64
from test_series import test_series

ALLOWED_EXTENSIONS = set(['gif','png','jpg','jpeg', 'txt', 'c', 'cc', 'cpp', 'C', 'java', 'php', 'py', 'rb',
                          'zip', 'gz', 'bz2', '7z', 'pdf', 'epub', 'css', 'js', 'html', 'h', 'hh', 'hpp', 'svg',
                          'tar.gz', 'tar.bz2', 'tgz', 'tbz', 'doc', 'docx', 'odf', 'odt', 'ppt', 'pptx', 'djvu'])

kunjika = Flask(__name__)

kunjika.config.from_object('config')
DB_URL = kunjika.config['DB_URL']
HOST_URL = kunjika.config['HOST_URL']
ES_URL = kunjika.config['ES_URL']
MAIL_SERVER_IP  = kunjika.config['MAIL_SERVER_IP']
kunjika.debug = kunjika.config['DEBUG_MODE']
kunjika.add_url_rule('/uploads/<filename>', 'uploaded_file',
                     build_only=True)
kunjika.wsgi_app = SharedDataMiddleware(kunjika.wsgi_app, {
    '/uploads': kunjika.config['UPLOAD_FOLDER']})
QUESTIONS_PER_PAGE = kunjika.config['QUESTIONS_PER_PAGE']
TAGS_PER_PAGE = kunjika.config['TAGS_PER_PAGE']
USERS_PER_PAGE = kunjika.config['USERS_PER_PAGE']
#GROUPS_PER_PAGE = kunjika.config['GROUPS_PER_PAGE']

USER_QUESTIONS_PER_PAGE = kunjika.config['USER_QUESTIONS_PER_PAGE']
USER_ANSWERS_PER_PAGE = kunjika.config['USER_ANSWERS_PER_PAGE']

ARTICLES_PER_PAGE = kunjika.config['ARTICLES_PER_PAGE']

is_maintenance_mode = kunjika.config['MAINTENANCE_MODE']

oid = OpenID(kunjika, '/tmp')

mail = Mail(kunjika)
admin = kunjika.config['ADMIN_EMAIL']

kunjika.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='kunjika.libreprogramming.org',
	MAIL_PORT=25,
	MAIL_USE_TLS=True,
	MAIL_USERNAME = 'noreply@kunjika.libreprogramming.org',
	MAIL_PASSWORD = ''
	)
lm = LoginManager()
lm.init_app(kunjika)
lm.session_protection = "strong"

cb = Couchbase.connect("default")
qb = Couchbase.connect("questions")
tb = Couchbase.connect("tags")
pb = Couchbase.connect("polls")
kb = Couchbase.connect("kunjika")

es_conn = pyes.ES(ES_URL)

#Initialize count at first run. Later it is useless
try:
    cb.add('count', 0)
except:
    pass

#Initialize question count at first run. Later it is useless
try:
    qb.add('qcount', 0)
except:
    pass

#Initialize question count at first run. Later it is useless
try:
    tb.add('tcount', 0)
except:
    pass

# Initialize indices for different buckets
try:
    #es_conn.indices.delete_index("questions")
    es_conn.indices.create_index("questions")
except:
    pass

try:
    #es_conn.indices.delete_index("users")
    es_conn.indices.create_index("users")
except:
    pass

try:
    #es_conn.indices.delete_index("tags")
    es_conn.indices.create_index("tags")
except:
    pass

try:
    #es_conn.indices.delete_index("tags")
    es_conn.indices.create_index("articles")
except:
    pass

questions_mapping = {
     'title': {
         'boost': 1.0,
         'index': 'analyzed',
         'store': 'yes',
         'type': 'string',
         "term_vector": "with_positions_offsets"
     },
     'description': {
         'boost': 1.0,
         'index': 'analyzed',
         'store': 'yes',
         'type': 'string',
         "term_vector": "with_positions_offsets"
     },
     'qid': {
         'boost': 1.0,
         'index': 'not_analyzed',
         'store': 'yes',
         'type': 'integer',
         "term_vector": "with_positions_offsets"
     }
}

users_mapping = {
     'name': {
         'boost': 1.0,
         'index': 'analyzed',
         'store': 'yes',
         'type': 'string',
         "term_vector": "with_positions_offsets"
     },
     'uid': {
         'boost': 1.0,
         'index': 'not_analyzed',
         'store': 'yes',
         'type': 'integer',
         "term_vector": "with_positions_offsets"
     }
}

tags_mapping = {
     'tag': {
         'boost': 1.0,
         'index': 'analyzed',
         'store': 'yes',
         'type': 'string',
         "term_vector": "with_positions_offsets"
     },
     'tid': {
         'boost': 1.0,
         'index': 'not_analyzed',
         'store': 'yes',
         'type': 'integer',
         "term_vector": "with_positions_offsets"
     }
}

articles_mapping = {
     'title': {
         'boost': 1.0,
         'index': 'analyzed',
         'store': 'yes',
         'type': 'string',
         "term_vector": "with_positions_offsets"
     },
     'content': {
         'boost': 1.0,
         'index': 'analyzed',
         'store': 'yes',
         'type': 'string',
         "term_vector": "with_positions_offsets"
     },
     'qid': {
         'boost': 1.0,
         'index': 'not_analyzed',
         'store': 'yes',
         'type': 'string',
         "term_vector": "with_positions_offsets"
     }
}

es_conn.indices.put_mapping("questions-type", {'properties':questions_mapping}, ["questions"])
es_conn.indices.put_mapping("users-type", {'properties':users_mapping}, ["users"])
es_conn.indices.put_mapping("tags-type", {'properties':tags_mapping}, ["tags"])
es_conn.indices.put_mapping("articles-type", {'properties':articles_mapping}, ["articles"])

gravatar32 = Gravatar(kunjika,
                      size=32,
                      rating='g',
                      default='identicon',
                      force_default=False,
                      force_lower=False)

gravatar100 = Gravatar(kunjika,
                       size=100,
                       rating='g',
                       default='identicon',
                       force_default=False,
                       force_lower=False)

bcrypt = Bcrypt(kunjika)

lm.anonymous_user = Anonymous

kunjika.jinja_env.globals['url_for_other_page'] = utility.url_for_other_page
kunjika.jinja_env.globals['url_for_other_user_question_page'] = utility.url_for_other_user_question_page
kunjika.jinja_env.globals['url_for_other_user_answer_page'] = utility.url_for_other_user_answer_page
kunjika.jinja_env.globals['url_for_search_page'] = utility.url_for_search_page

if not kunjika.debug:
    import logging
    from logging.handlers import RotatingFileHandler, SMTPHandler
    file_handler = RotatingFileHandler(kunjika.config['LOG_FILE'], mode='a',
                                       maxBytes=kunjika.config['MAX_LOG_SIZE'],
                                       backupCount=kunjika.config['BACKUP_COUNT'])
    file_handler.setLevel(logging.WARNING)
    kunjika.logger.addHandler(file_handler)

    mail_handler = SMTPHandler(MAIL_SERVER_IP,
                               kunjika.config['ADMIN_EMAIL'],
                               kunjika.config['ADMIN_EMAIL'], 'Application Failed')
    mail_handler.setLevel(logging.ERROR)
    kunjika.logger.addHandler(mail_handler)

@kunjika.before_request
def check_for_maintenance():
    if is_maintenance_mode and request.path != url_for('maintenance'):
        return redirect(url_for('maintenance'))


@kunjika.route('/maintenance')
def maintenance():
    return 'Sorry, off for maintenance!', 503

@kunjika.before_request
def before_request():
    g.user = current_user

def get_user(uid):
    try:
        user_from_db = cb.get(str(uid)).value
        if 'role' in user_from_db:
            return User(user_from_db['name'], user_from_db, user_from_db['id'], user_from_db['role'])
        else:
            return User(user_from_db['name'], user_from_db, user_from_db['id'], None)
    except NotFoundError:
        return None

@lm.user_loader
def load_user(uid):
    ###print id
    user = get_user(int(uid))
    return user

@kunjika.route('/', defaults={'page': 1}, methods=['GET', 'POST'])
@kunjika.route('/questions', defaults={'page': 1}, methods=['GET', 'POST'])
@kunjika.route('/questions/<qid>', methods=['GET', 'POST'])
@kunjika.route('/questions/<qid>/<url>', methods=['GET', 'POST'])
@kunjika.route('/questions/page/<int:page>')
@kunjika.route('/questions/tagged/<string:tag>', defaults={'page': 1}, methods=['GET', 'POST'])
@kunjika.route('/questions/tagged/<string:tag>/page/<int:page>')
def questions(tag=None, page=None, qid=None, url=None):
    if not g.user.is_authenticated() and 'displayed' not in session:
        flash('First time here. Consider joining and helping community.', 'info')
        session['displayed'] = True

    tag_list = []
    (qcount, acount, tcount, ucount, tag_list) = utility.common_data()

    questions_dict = {}
    if tag is not None:
	print tag
        [questions_list, count] = utility.get_questions_for_tag(page, QUESTIONS_PER_PAGE, tag)
        if not questions_list and page != 1:
            abort(404)
        pagination = utility.Pagination(page, QUESTIONS_PER_PAGE, count)
        if g.user is None:
            return render_template('questions.html', title='Questions', qpage=True, questions=questions_list,
                                   pagination=pagination, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)
        elif g.user is not None and g.user.is_authenticated():
            return render_template('questions.html', title='Questions', qpage=True, questions=questions_list,
                                   name=g.user.name, role=g.user.role, user_id=g.user.id, pagination=pagination, qcount=qcount,
                                   ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)
        else:
            return render_template('questions.html', title='Questions', qpage=True, questions=questions_list,
                                   pagination=pagination, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)
    if qid is None:
        count = qb.get('qcount').value
        questions_list = utility.get_questions_for_page(page, QUESTIONS_PER_PAGE, count)
        if not questions_list and page != 1:
            abort(404)
        pagination = utility.Pagination(page, QUESTIONS_PER_PAGE, count)
        #questions_list = question.get_questions()
        if g.user is None:
            return render_template('questions.html', title='Questions', qpage=True, questions=questions_list,
                                   pagination=pagination, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)
        elif g.user is not None and g.user.is_authenticated():
            return render_template('questions.html', title='Questions', qpage=True, questions=questions_list,
                                   name=g.user.name, role=g.user.role, user_id=g.user.id, pagination=pagination, qcount=qcount,
                                   ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)
        else:
            return render_template('questions.html', title='Questions', qpage=True, questions=questions_list,
                                   pagination=pagination, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)
    else:
        questions_dict = question.get_question_by_id(qid, questions_dict)

        if request.referrer == HOST_URL + "questions":
            questions_dict['views'] += 1
        elif request.host_url != HOST_URL + "":
            questions_dict['views'] += 1
        choices = []
        votes = []
        j = 0
        #print questions_dict['qid']
        similar_questions = utility.get_similar_questions(questions_dict['title'], questions_dict['qid'])
        if 'options' in questions_dict['content']:
            for option in questions_dict['content']['options']:
                choices.append((option, option))
                j += 1
                if j == 1:
                    option1_votes = urllib2.urlopen(
                        DB_URL + 'polls/_design/dev_qa/_view/get_option1_votes?key=' + '"' + qid + '"' + '&reduce=true'
                    ).read()
                    option1_votes = json.loads(option1_votes)
                    if len(option1_votes['rows']) != 0:
                        option1_votes = option1_votes['rows'][0]['value']
                    else:
                        option1_votes = 0
                    votes.append((option1_votes, option))
                elif j == 2:
                    option2_votes = urllib2.urlopen(
                        DB_URL + 'polls/_design/dev_qa/_view/get_option2_votes?key=' + '"' + qid + '"' + '&reduce=true'
                    ).read()
                    option2_votes = json.loads(option2_votes)
                    if len(option2_votes['rows']) != 0:
                        option2_votes = option2_votes['rows'][0]['value']
                    else:
                        option2_votes = 0
                    votes.append((option2_votes, option))
                    #print option2_votes
                    #print option
                elif j == 3:
                    option3_votes = urllib2.urlopen(
                        DB_URL + 'polls/_design/dev_qa/_view/get_option3_votes?key=' + '"' + qid + '"' + '&reduce=true'
                    ).read()
                    option3_votes = json.loads(option3_votes)
                    if len(option3_votes['rows']) != 0:
                        option3_votes = option3_votes['rows'][0]['value']
                    else:
                        option3_votes = 0
                    votes.append((option3_votes, option))
                elif j == 4:
                    option4_votes = urllib2.urlopen(
                        DB_URL + 'polls/_design/dev_qa/_view/get_option4_votes?key=' + '"' + qid + '"' + '&reduce=true'
                    ).read()
                    option4_votes = json.loads(option4_votes)
                    if len(option4_votes['rows']) != 0:
                        option4_votes = option4_votes['rows'][0]['value']
                    else:
                        option4_votes = 0
                    votes.append((option4_votes, option))
                elif j == 5:
                    option5_votes = urllib2.urlopen(
                        DB_URL + 'polls/_design/dev_qa/_view/get_option5_votes?key=' + '"' + qid + '"' + '&reduce=true'
                    ).read()
                    option5_votes = json.loads(option5_votes)
                    if len(option5_votes['rows']) != 0:
                        option5_votes = option5_votes['rows'][0]['value']
                    else:
                        option5_votes = 0
                    votes.append((option5_votes, option))
                elif j == 6:
                    option6_votes = urllib2.urlopen(
                        DB_URL + 'polls/_design/dev_qa/_view/get_option6_votes?key=' + '"' + qid + '"' + '&reduce=true'
                    ).read()
                    option6_votes = json.loads(option6_votes)
                    if len(option6_votes['rows']) != 0:
                        option6_votes = option6_votes['rows'][0]['value']
                    else:
                        option6_votes = 0
                    votes.append((option6_votes, option))
                elif j == 7:
                    option7_votes = urllib2.urlopen(
                        DB_URL + 'polls/_design/dev_qa/_view/get_option7_votes?key=' + '"' + qid + '"' + '&reduce=true'
                    ).read()
                    option7_votes = json.loads(option7_votes)
                    if len(option7_votes['rows']) != 0:
                        option7_votes = option7_votes['rows'][0]['value']
                    else:
                        option7_votes = 0
                    votes.append((option7_votes, option))
                elif j == 8:
                    option8_votes = urllib2.urlopen(
                        DB_URL + 'polls/_design/dev_qa/_view/get_option8_votes?key=' + '"' + qid + '"' + '&reduce=true'
                    ).read()
                    option8_votes = json.loads(option8_votes)
                    if len(option8_votes['rows']) != 0:
                        option8_votes = option8_votes['rows'][0]['value']
                    else:
                        option8_votes = 0
                    votes.append((option8_votes, option))
                elif j == 9:
                    option9_votes = urllib2.urlopen(
                        DB_URL + 'polls/_design/dev_qa/_view/get_option9_votes?key=' + '"' + qid + '"' + '&reduce=true'
                    ).read()
                    option9_votes = json.loads(option9_votes)
                    if len(option9_votes['rows']) != 0:
                        option9_votes = option9_votes['rows'][0]['value']
                    else:
                        option9_votes = 0
                    votes.append((option9_votes, option))
                elif j == 10:
                    option10_votes = urllib2.urlopen(
                        DB_URL + 'polls/_design/dev_qa/_view/get_option10_votes?key=' + '"' + qid + '"' + '&reduce=true'
                    ).read()
                    option10_votes = json.loads(option10_votes)
                    if len(option10_votes['rows']) != 0:
                        option10_votes = option10_votes['rows'][0]['value']
                    else:
                        option10_votes = 0
                    votes.append((option10_votes, option))
        if g.user is AnonymousUserMixin:
            return render_template('single_question.html', title='Questions', qpage=True, questions=questions_dict)
        elif g.user is not None and g.user.is_authenticated():
            user = cb.get(str(g.user.id)).value
            if 'mc' not in questions_dict['content'] and 'sc' not in questions_dict['content']:
                answerForm = AnswerForm(request.form)
                if answerForm.validate_on_submit() and request.method == 'POST':
                    '''
                    try:
                        data = sb.get(user['email'])
                        data['answers/min'] += 1
                        data['answers/hr'] += 1
                        data['answers/day'] += 1
                        sb.replace(user['email'] + 'answers/min', data, ttl=60)
                        sb.replace(user['email'] + 'answers/hr', data, ttl=3600)
                        sb.replace(user['email'] + 'answers/day', data, ttl=86400)
                        if data['answers/min'] >= kunjika.config['ANSWERS_PER_MIN'] or \
                            data['answers/hr'] >= kunjika.config['ANSWERS_PER_HR'] or \
                            data['answers/day'] >= kunjika.config['ANSWERS_PER_DAY']:

                            return redirect(url_for('questions'))

                    except:
                        data1 = {}
                        data1['email'] = user['email']
                        data1['answers/min'] = 1
                        data1['answers/hr'] = 1
                        data1['answers/day'] = 1
                        sb.add(user['email'] + 'answers/min', data1, ttl=60)
                        sb.add(user['email'] + 'answers/hr', data1, ttl=3600)
                        sb.add(user['email'] + 'answers/day', data1, ttl=86400)
                    '''
                    answer = {}
                    if 'answers' in questions_dict:
                        answer['aid'] = questions_dict['acount'] + 1
                        answer['answer'] = answerForm.answer.data
                        answer['poster'] = g.user.id
                        answer['ts'] = int(time())
                        answer['votes'] = 0
                        answer['ip'] = request.remote_addr
                        answer['best'] = False
                        answer['votes_list'] = []
                        questions_dict['acount'] += 1

                        questions_dict['answers'].append(answer)
                        # Isuue 9
                        #user['answers'].append(str(qid) + '-' + str(answer['aid']))
                        user['acount'] += 1

                    else:
                        answer['aid'] = 1
                        answer['answer'] = answerForm.answer.data
                        answer['poster'] = g.user.id
                        answer['ts'] = int(time())
                        answer['votes'] = 0
                        answer['ip'] = request.remote_addr
                        answer['best'] = False
                        answer['votes_list'] = []
                        questions_dict['acount'] = 1

                        questions_dict['answers'] = []
                        questions_dict['answers'].append(answer)
                        # Issue 9
                        #user['answers'].append(str(qid) + '-' + str(answer['aid']))
                        user['acount'] += 1

                    questions_dict['updated'] = int(time())
                    user['rep'] += 4
                    cb.replace(str(g.user.id), user)
                    qb.replace(str(questions_dict['qid']), questions_dict)

                    email_list = []
                    email_list.append(str(questions_dict['content']['op']))
                    if 'comments' in questions_dict:
                        for comment in questions_dict['comments']:
                            email_list.append(str(comment['poster']))
                    if 'answers' in questions_dict:
                        for answer in questions_dict['answers']:
                            email_list.append(str(answer['poster']))
                            if 'comments' in answer:
                                for comment in answer['comments']:
                                    email_list.append(str(comment['poster']))

                    email_list = set(email_list)
                    current_user_list = [str(g.user.id)]
                    email_list = email_list - set(current_user_list)
                    email_list = list(email_list)
                    email_users = None
                    if email_list:
                        email_users = cb.get_multi(email_list)
                    email_list = []
                    if email_users is not None:
                        for id in email_users:
                            email_list.append(email_users[str(id)].value['email'])

                        msg = Message("A new answer has been posted to a question where you have answered or commented")
                        msg.recipients = email_list
                        msg.sender = admin
                        msg.html = "<p>Hi,<br/><br/> A new answer has been posted which you can read at " +\
                        HOST_URL + "questions/" + str(questions_dict['qid']) + '/' + questions_dict['content']['url'] + \
                        " <br/><br/>Best regards,<br/>Kunjika Team<p>"
                        mail.send(msg)

                    return redirect(url_for('questions', qid=questions_dict['qid'], url=questions_dict['content']['url']))
                qb.replace(str(questions_dict['qid']), questions_dict)

                return render_template('single_question.html', title='Questions', qpage=True, questions=questions_dict,
                                       form=answerForm, name=g.user.name, role=g.user.role, user_id=unicode(g.user.id), gravatar=gravatar32,
                                       qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list,
                                       similar_questions=similar_questions)
            elif 'sc' in questions_dict['content']:
                class PollForm(Form):
                    pass


                #print str(votes)
                setattr(PollForm, 'radio', RadioField('radio', choices=choices))
                answerForm=PollForm(request.form)
                if answerForm.validate_on_submit() and request.method == 'POST':

                    vote = {}
                    questions_dict['acount'] += 1
                    poll_id = str(questions_dict['qid']) + '-' + str(g.user.id)

                    vote['qid'] = str(questions_dict['qid'])
                    vote['uid'] = str(g.user.id)

                    i = 0
                    for choice in choices:
                        i += 1
                        if i == 1 and choice[0] == str(answerForm.radio.data):
                            vote['option1'] = True
                        elif i == 2 and choice[0] == str(answerForm.radio.data):
                            vote['option2'] = True
                        elif i == 3 and choice[0] == str(answerForm.radio.data):
                            vote['option3'] = True
                        elif i == 4 and choice[0] == str(answerForm.radio.data):
                            vote['option4'] = True
                        elif i == 5 and choice[0] == str(answerForm.radio.data):
                            vote['option5'] = True
                        elif i == 6 and choice[0] == str(answerForm.radio.data):
                            vote['option6'] = True
                        elif i == 7 and choice[0] == str(answerForm.radio.data):
                            vote['option7'] = True
                        elif i == 8 and choice[0] == str(answerForm.radio.data):
                            vote['option8'] = True
                        elif i == 9 and choice[0] == str(answerForm.radio.data):
                            vote['option9'] = True
                        elif i == 10 and choice[0] == str(answerForm.radio.data):
                            vote['option10'] = True

                    if 'poll_votes' in user:
                        user['poll_votes'] += 1
                    else:
                        user['poll_votes'] = 1

                    questions_dict['updated'] = int(time())
                    user['rep'] += 4

                    try:
                        pb.add(poll_id, vote)
                        cb.replace(str(g.user.id), user)
                        qb.replace(str(questions_dict['qid']), questions_dict)
                    except:
                        flash('You have already voted on this question', 'error')

                    return redirect(url_for('questions', qid=questions_dict['qid'], url=questions_dict['content']['url']))
                qb.replace(str(questions_dict['qid']), questions_dict)
                return render_template('single_question.html', title='Questions', qpage=True, questions=questions_dict,
                                       form=answerForm, name=g.user.name, role=g.user.role, user_id=unicode(g.user.id), gravatar=gravatar32,
                                       qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list,
                                       votes=votes, similar_questions=similar_questions)
            elif 'mc' in questions_dict['content']:
                class PollForm(Form):
                    pass
                options = []
                i = 0
                for option in questions_dict['content']['options']:
                    i += 1
                    setattr(PollForm, 'option' + str(i), BooleanField('option'+str(i)))
                    options.append(option)
                i += 1
                setattr(PollForm, 'option' + str(i), BooleanField('option'+str(i)))
                options.append(option)
                answerForm=PollForm(request.form)
                if answerForm.validate_on_submit() and request.method == 'POST':
                    i = 0
                    vote = {}
                    for option in questions_dict['content']['options']:
                        i += 1
                        if i == 1:
                            vote['option1'] = answerForm.option1.data
                        elif i == 2:
                            vote['option2'] = answerForm.option2.data
                        elif i == 3:
                            vote['option3'] = answerForm.option3.data
                        elif i == 4:
                            vote['option4'] = answerForm.option4.data
                        elif i == 5:
                            vote['option5'] = answerForm.option5.data
                        elif i == 6:
                            vote['option6'] = answerForm.option6.data
                        elif i == 7:
                            vote['option7'] = answerForm.option7.data
                        elif i == 8:
                            vote['option8'] = answerForm.option8.data
                        elif i == 9:
                            vote['option9'] = answerForm.option9.data
                        elif i == 10:
                            vote['option10'] = answerForm.option10.data

                    questions_dict['acount'] += 1

                    if 'poll_votes' in user:
                        user['poll_votes'] += 1
                    else:
                        user['poll_votes'] = 1

                    poll_id = str(questions_dict['qid']) + '-' + str(g.user.id)

                    vote['qid'] = str(questions_dict['qid'])
                    vote['uid'] = str(g.user.id)
                    questions_dict['updated'] = int(time())
                    user['rep'] += 4

                    try:
                        pb.add(poll_id, vote)
                        cb.replace(str(g.user.id), user)
                        qb.replace(str(questions_dict['qid']), questions_dict)
                    except:
                        flash('You have already voted on this question', 'error')

                    return redirect(url_for('questions', qid=questions_dict['qid'], url=questions_dict['content']['url']))
                qb.replace(str(questions_dict['qid']), questions_dict)
                return render_template('single_question.html', title='Questions', qpage=True, questions=questions_dict,
                                       form=answerForm, name=g.user.name, role=g.user.role, user_id=unicode(g.user.id), gravatar=gravatar32,
                                       qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list,
                                       options=i, field_names=options, votes=votes, similar_questions=similar_questions)


        else:
            qb.replace(str(questions_dict['qid']), questions_dict)
            return render_template('single_question.html', title='Questions', qpage=True, questions=questions_dict,
                                   qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list,
                                   votes=votes, similar_questions=similar_questions)

@kunjika.route('/users/<uid>', defaults={'qpage': 1, 'apage': 1})
@kunjika.route('/users/<uid>/<path:uname>', defaults={'qpage': 1, 'apage': 1})
@kunjika.route('/users/<uid>/<path:uname>/<int:qpage>/<int:apage>')
def users(qpage=None, apage=None, uid=None, uname=None):
    (qcount, acount, tcount, ucount, tag_list) = utility.common_data()
    print uname
    user = cb.get(str(uid)).value
    questions = utility.get_user_questions_per_page(user, qpage, USER_QUESTIONS_PER_PAGE, user['qcount'])
    if not questions and qpage != 1:
        abort(404)
    # answers is actually questions containing answers
    answers, aids = utility.get_user_answers_per_page(user, apage, USER_ANSWERS_PER_PAGE, user['acount'])
    if not answers and apage != 1:
        abort(404)
    question_pagination = utility.Pagination(qpage, USER_QUESTIONS_PER_PAGE, user['qcount'])
    answer_pagination = utility.Pagination(apage, USER_ANSWERS_PER_PAGE, user['acount'])
    #user = json.loads(user)
    gravatar100 = Gravatar(kunjika,
                           size=100,
                           rating='g',
                           default='identicon',
                           force_default=False,
                           force_lower=False)
    if 'skills' in user:
        user['skills'] = user['skills'].sort()
    if uid in session:
        logged_in = True
	if g.user.is_authenticated():
	        return render_template('users.html', title=user['name'], user_id=user['id'], name=user['name'], fname=user['fname'], \
        	                       lname=user['lname'], email=user['email'], gravatar=gravatar100, logged_in=logged_in, \
                	               upage=True, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list, user=user, \
                        	       questions=questions, answers=answers, aids=aids, question_pagination=question_pagination, \
					answer_pagination=answer_pagination, role=g.user.role) 
    return render_template('users.html', title=user['name'], user_id=user['id'], lname=user['lname'], name=user['name'], fname=user['fname'], email=user['email'], gravatar=gravatar100, upage=True,
                           qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list, user=user,
                           questions=questions, answers=answers, aids=aids, question_pagination=question_pagination,
                           answer_pagination=answer_pagination)

@kunjika.route('/ask', methods=['GET', 'POST'])
def ask():
    (qcount, acount, tcount, ucount, tag_list) = utility.common_data()
    questionForm = QuestionForm(request.form)
    if g.user is not None and g.user.is_authenticated():
        user = cb.get(str(g.user.id)).value
        if questionForm.validate_on_submit() and request.method == 'POST':
            data1 = {}
	    '''
            try:

                data = sb.get(user['email'])
                data['questions/min'] += 1
                data['questions/hr'] += 1
                data['questions/day'] += 1
                sb.replace(user['email'] + 'questions/min', data, ttl=60)
                sb.replace(user['email'] + 'questions/hr', data, ttl=3600)
                sb.replace(user['email'] + 'questions/day', data, ttl=86400)
                if data['questions/min'] >= kunjika.config['QUESTIONS_PER_MIN'] or \
                    data['questions/hr'] >= kunjika.config['QUESTIONS_PER_HR'] or \
                    data['questions/day'] >= kunjika.config['QUESTIONS_PER_DAY']:

                    return redirect(url_for('questions'))

            except:
                data1['email'] = user['email']
                data1['questions/min'] = 1
                data1['questions/hr'] = 1
                data1['questions/day'] = 1
                sb.add(user['email'] + 'questions/min', data1, ttl=60)
                sb.add(user['email'] + 'questions/hr', data1, ttl=3600)
                sb.add(user['email'] + 'questions/day', data1, ttl=86400)
	    '''

            question = {}
            question['content'] = {}
            title = questionForm.question.data
            question['content']['description'] = questionForm.description.data
            question['content']['tags'] = []
            question['content']['tags'] = questionForm.tags.data.split(',')
            question['content']['tags'] = [tag.strip(' \t').lower() for tag in question['content']['tags']]
            tag_list = []
            new_tag_list = []
            for tag in question['content']['tags']:
                tag = list(tag)
                for i in range(0, len(tag)):
                    if tag[i] == '`' or tag[i] == '~' or tag[i] == '!' or tag[i] == '@' or tag[i] == '#' \
                         or tag[i] == '$' or tag[i] == '%' or tag[i] == '^' or tag[i] == '&' or tag[i] == '+' \
                         or tag[i] == '+'  or tag[i] ==  '{' or tag[i] == '[' or tag[i] == ']' or tag[i] == '}' \
                         or tag[i] == '\\' or tag[i] == '|' or tag[i] == ':' or tag[i] == ';' or tag[i] == '\''\
                         or tag[i] == '<' or tag[i] == '>' or tag[i] == ',' or tag[i] == '?' or tag[i] == '/'\
                         or tag[i] == ' ':
                        tag[i] = '-'
                tag_list.append(''.join(tag))

            for tag in tag_list:
                try:
                    tag = urllib2.urlopen(DB_URL + 'tags/_design/dev_qa/_view/get_tag_by_id?stale=false&key=' + urllib2.quote(str(tag))).read()
                    tid = json.loads(tag)['rows'][0]['id']
                    tag = tb.get(str(tid)).value
                    new_tag_list.append(tag['tag'])

                except:
                    ##print "hello"
                    new_tag_list.append(tag)

            question['content']['tags'] = new_tag_list

            question['title'] = title

            url = utility.generate_url(title)

            question['content']['url'] = url
            question['content']['op'] = str(g.user.id)
            question['content']['ts'] = int(time())
            question['updated'] = question['content']['ts']
            question['content']['ip'] = request.remote_addr
            question['qid'] = qb.incr('qcount', 1).value
            question['votes'] = 0
            question['acount'] = 0
            question['views'] = 0
            question['votes_list'] = []
            question['opname'] = g.user.name
            question['close'] = False

            user = cb.get(str(g.user.id)).value

            user['rep'] += 1
            #Isuue 9
            #user['questions'].append(question['qid'])
            user['qcount'] += 1
            print question['qid']
            es_conn.index({'title':title, 'description':question['content']['description'], 'qid':question['qid'],
                           'position':question['qid']}, 'questions', 'questions-type', question['qid'])
            es_conn.indices.refresh('questions')
            qb.add(str(question['qid']), question)

            cb.replace(str(g.user.id), user)


            add_tags(question['content']['tags'], question['qid'])

            return redirect(url_for('questions', qid=question['qid'], url=question['content']['url']))

        return render_template('ask.html', title='Ask', form=questionForm, apage=True, name=g.user.name, role=g.user.role,
                               user_id=g.user.id, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)
    return redirect(url_for('login'))

def populate_user_fields(data, form):

    data['email'] = form.email1.data
    data['fname'] = form.fname.data
    data['lname'] = form.lname.data
    data['name'] = data['fname'] + " " + data['lname']
    data['rep'] = 0
    data['banned'] = False
    data['votes_count'] = {}
    data['votes_count']['up'] = 0
    data['votes_count']['down'] = 0
    data['votes_count']['question'] = 0
    data['votes_count']['answers'] = 0
    data['acount'] = 0
    data['qcount'] = 0
    data['questions'] = []
    data['answers'] = []
    data['votes'] = []
    data['website'] = ''
    data['location'] = ''
    data['about-me'] = ''
    data['receive-emails'] = True
    #data['receive-invites'] = True

@kunjika.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    #if request.args.get('email') is None:
    #    return redirect('/')
    document = None
    profileForm = ProfileForm(request.form)
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('questions'))
    if profileForm.validate_on_submit() and request.method == 'POST':
        ##print "hello"
        data = {}
        ##print profileForm.email1.data
        view = urllib2.urlopen(DB_URL + 'default/_design/dev_qa/_view/get_role?stale=false').read()
        view = json.loads(view)

        if len(view['rows']) == 0:
            ##print "hello1"
            data['role'] = 'admin'
            populate_user_fields(data, profileForm)

            did = cb.incr('count', 1).value
            data['id'] = did
            cb.add(str(did), data)
            user = User(data['name'], data, data['id'])
            login_user(user, remember=True)
            es_conn.index({'name':data['name'], 'uid':did, 'position':did}, 'users', 'users-type', did)
            es_conn.indices.refresh('users')
            g.user = user
            try:
                msg = Message("Registration at Kunjika")
                msg.recipients = [data['email']]
                msg.sender = admin
                msg.html = "<p>Hi,<br/> Thanks for registering at kunjika. Congratulations on" \
                           "being the first user. Since you are the first by default you are admin" \
                           ".<br/>Best regards,<br/>Kunjika Team<p>"
                mail.send(msg)

                return redirect(url_for('questions'))
            except:
                return make_response("cant login")

        document = urllib2.urlopen(
            DB_URL + 'default/_design/dev_qa/_view/get_id_from_email?key=' + '"' + profileForm.email1.data + '"&stale=false').read()
        document = json.loads(document)
        #if 'id' in document['rows'][0]:
        #    document = cb.get(document['rows'][0]['id']).value
        ###print(document)
        if len(document['rows']) == 0:
            ##print "hello2"
            populate_user_fields(data, profileForm)

            did = cb.incr('count', 1).value
            data['id'] = did
            cb.add(str(did), data)
            user = User(data['name'], data, did)
            login_user(user, remember=True)
            ##print data['name'] + ' ' + did
            es_conn.index({'name':data['name'], 'uid':did, 'position':did}, 'users', 'users-type', did)
            es_conn.indices.refresh('users')
            g.user = user
            try:
                msg = Message("Registration at Kunjika")
                msg.recipients = [data['email']]
                msg.sender = admin
                msg.html = "<p>Hi,<br/> Thanks for registering at kunjika. If you have not " \
                           "registered please email at " + admin + " .<br/>Best regards," \
                                                                  "<br/> Admin<p>"
                mail.send(msg)

                return redirect(url_for('questions'))
            except:
                return make_response("cant login")
        #else:
        #  document = cb.get(document['rows'][0]['id']).value
    return render_template('create_profile.html', form=profileForm,
                           title="Create Profile", lpage=True, next=oid.get_next_url())

@oid.after_login
def create_or_login(resp):
    session['openid'] = resp.identity_url
    user = utility.filter_by(resp.email)
    ##print user
    if user is not None:
        if user['banned'] == True:
            return redirect(url_for('questions'))
        flash(u'Successfully signed in')

        ##print user
        session[user['id']] = user['id']
        session['logged_in'] = True
        if 'role' in user:
            user['admin'] = True

        g.user = User(user['name'], user, user['id'])
        user = g.user   
        #user = User(user['name'], user, user['id'])
        try:
            login_user(user, remember=True)
            return redirect(url_for('questions'))
        except:
            return make_response("cant login")
    return redirect(url_for('create_profile', next=oid.get_next_url(),
                            name=resp.fullname or resp.nickname,
                            email=resp.email))

@kunjika.route('/openid_login', methods=['GET', 'POST'])
@oid.loginhandler
def openid_login():
    registrationForm = RegistrationForm(request.form)
    loginForm = LoginForm(request.form)

    ##print g.user

    if g.user is not AnonymousUserMixin and g.user.is_authenticated():
        return redirect(oid.get_next_url())
    if request.method == 'POST':
        openid = request.form.get('openid_identifier')
        return oid.try_login(openid, ask_for=['email', 'fullname', 'nickname'])
    return render_template('openid.html', form=registrationForm, loginForm=loginForm, title='Sign In',
                           lpage=True, next=oid.get_next_url(), error=oid.fetch_error())

@kunjika.route('/login', methods=['GET', 'POST'])
def login():
    registrationForm = RegistrationForm(request.form)
    loginForm = LoginForm(request.form)
    openidForm = OpenIDForm(request.form)

    if loginForm.validate_on_submit() and request.method == 'POST':
        try:
            #document = json.loads(document)
            document = urllib2.urlopen(
                DB_URL + 'default/_design/dev_qa/_view/get_id_from_email?stale=false&key=' + '"' + urllib2.quote(loginForm.email.data) + '"').read()
            document = json.loads(document)
            if 'id' in document['rows'][0]:
                document = cb.get(document['rows'][0]['id']).value
            if document['banned'] is True:
                flash('Your acount is banned possibly because you abused the system. Contact ' + admin +
                      'for more info.', 'error')
                return redirect(url_for('questions'))
            if bcrypt.check_password_hash(document['password'], loginForm.password.data):
                session[document['id']] = document['id']
                session['logged_in'] = True
                if 'role' in document:
                    session['admin'] = True
                user = User(document['name'], document, document['id'])
                try:
                    login_user(user, remember=True)
                    flash('You have successfully logged in.', 'success')
                    g.user = user
                    return redirect(url_for('questions'))
                except:
                    return make_response("cant login")

            else:
                try:
                    user = kb.get(document['email'])
                    flash('Either email or password is wrong.', 'error')
                    user['login_attemps'] += 1
                    kb.replace(user['email'], user, ttl=600)
                    if user['login_attempts'] == kunjika.config['MAX_FAILED_LOGINS']:
                        document['password'] = kunjika.config['RESET_PASSWORD']
                        msg = Message("Account banned")
                        msg.recipients = [user['email']]
                        msg.sender = admin
                        msg.html = "<p>Hi,<br/> Your account has been banned because more than " + kunjika.config['MAX_FAILED_LOGINS'] + " attempts " \
                           "of login have failed in 10 minutes. Please reset your password to login. <br/>Best regards," \
                                                                  "<br/> Admin<p>"
                        mail.send(msg)
                except:
                    user = {}
                    user['email'] = document['email']
                    user['login_attempts'] = 1
                    kb.add(user['email'], user, ttl=600)
                    flash('Either email or password is wrong.', 'error')

                render_template('login.html', form=registrationForm, loginForm=loginForm, openidForm=openidForm, title='Sign In',
                                lpage=True, next=oid.get_next_url(), error=oid.fetch_error())

        except:
            return render_template('login.html', form=registrationForm, loginForm=loginForm, openidForm=openidForm,
                                   title='Sign In', lpage=True,
                                   next=oid.get_next_url(), error=oid.fetch_error())


    else:
        render_template('login.html', form=registrationForm, loginForm=loginForm, openidForm=openidForm, title='Sign In',
                        lpage=True, next=oid.get_next_url(),error=oid.fetch_error())

    return render_template('login.html', form=registrationForm, loginForm=loginForm, openidForm=openidForm, title='Sign In',
                           lpage=True, next=oid.get_next_url(), error=oid.fetch_error())


@kunjika.route('/register', methods=['POST'])
def register():
    loginForm = LoginForm(request.form)
    registrationForm = RegistrationForm(request.form)
    openidForm = OpenIDForm(request.form)
    document = None

    if registrationForm.validate_on_submit() and request.method == 'POST':
        passwd_hash = bcrypt.generate_password_hash(registrationForm.password.data)

        data = {}
        view = urllib2.urlopen(DB_URL + 'default/_design/dev_qa/_view/get_role?stale=false').read()
        view = json.loads(view)
        if len(view['rows']) == 0:
            data['password'] = passwd_hash
            data['role'] = 'admin'
            populate_user_fields(data, registrationForm)

            did = cb.incr('count', 1).value
            data['id'] = did
            cb.add(str(did), data)
            session['admin'] = True
            user = User(data['name'], data, data['id'])
            login_user(user, remember=True)
            g.user = user
            es_conn.index({'name':data['name'], 'uid':did, 'position':did}, 'users', 'users-type', did)
            es_conn.indices.refresh('users')
            return redirect(url_for('questions'))

        document = urllib2.urlopen(
            DB_URL + 'default/_design/dev_qa/_view/get_id_from_email?key=' + '"' + registrationForm.email1.data + '"&stale=false').read()
        document = json.loads(document)
        if len(document['rows']) != 0:
            if 'id' in document['rows'][0]:
                document = cb.get(document['rows'][0]['id']).value
                #print(document)
        else:
            data['password'] = passwd_hash
            populate_user_fields(data, registrationForm)

            did = cb.incr('count', 1).value
            data['id'] = did
            cb.add(str(did), data)

            user = User(data['name'], data, did)
            try:
                login_user(user, remember=True)
                g.user = user
                es_conn.index({'name':data['name'], 'uid':did, 'position':did}, 'users', 'users-type', did)
                es_conn.indices.refresh('users')
                flash('Thanks for registration. We hope you enjoy your stay here too.', 'success')
                msg = Message("Registration at Kunjika")
                msg.recipients = [data['email']]
                msg.sender = admin
                msg.html = "<p>Hi,<br/> Thanks for registering at kunjika. If you have not " \
                           "registered please email at " + admin + " .<br/>Best regards," \
                                                                  "<br/> Admin<p>"
                mail.send(msg)

                return redirect(url_for('questions'))
            except:
                return make_response("cant login")

    return render_template('register.html', form=registrationForm, loginForm=loginForm, openidForm=openidForm,
                           title='Register', lpage=True,
                           next=oid.get_next_url(), error=oid.fetch_error())


@kunjika.route('/check_email', methods=['POST'])
def check_email():
    email = request.form['email']

    try:
        document = urllib2.urlopen(
            DB_URL + 'default/_design/dev_qa/_view/get_id_from_email?key=' + '"' + urllib2.quote(email) + '"&stale=false').read()
        document = json.loads(document)
        if 'id' in document['rows'][0]:
            try:
                document = cb.get(document['rows'][0]['id']).value
                return '0'
            except:
                '1'
        else:
            return '1'
    except:
        return '1'

@kunjika.route('/logout')
def logout():
    logout_user()
    resp = make_response(redirect(url_for('questions')))
    resp.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
    return resp


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@kunjika.route('/image_upload', methods=['POST'])
def image_upload():
    if request.method == 'POST':
        file = request.files['file']
        content = file.read()
        extension = file.filename.split(".")[-1]
        encoded_file = base64.b64encode(content)
        id = 'u-' + str(uuid1()) + "." + extension
        data = {}
        try:
            kb.add(id, {'content': encoded_file})
            data['success'] = "true"
            data['imagePath'] = HOST_URL + "uploads/" + id
        except:
            data['success'] = "false"
            data['mesage'] = "Invalid image file"

        return json.dumps(data)

@kunjika.route('/uploads/<string:filename>', methods=['GET'])
def get_uploads(filename):
    content = kb.get(filename).value['content']
    content = base64.b64decode(content)
    return content

'''
def image_upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            pathname = os.path.join(kunjika.config['UPLOAD_FOLDER'], filename)
            saved = False
            suffix = 0
            extension = os.path.splitext(basename(pathname))[1]
            filename = os.path.splitext(basename(filename))[0]
            f = filename
            new_filename = ""
            while saved is False:
                try:
                    with open(pathname):
                        suffix += 1
                        new_filename = f + '_' + str(suffix) + extension
                        new_pathname = os.path.join(kunjika.config['UPLOAD_FOLDER'], new_filename)
                        filename = new_filename
                        try:
                            with open(new_pathname):
                                next
                        except IOError:
                            file.save(new_pathname)
                            saved = True
                            break
                except IOError:
                    try:
                        file.save(pathname)
                        filename = os.path.splitext(basename(pathname))[0] + os.path.splitext(basename(pathname))[1]
                        saved = True
                        break
                    except IOError:
                        saved = False
                        break
            data = {}

            if saved is True:
                data['success'] = "true"
                data['imagePath'] = HOST_URL + "uploads/" + filename
            else:
                data['success'] = "false"
                data['mesage'] = "Invalid image file"

            return json.dumps(data)
'''

@kunjika.route('/get_tags/<qid>', methods=['GET', 'POST'])
@kunjika.route('/get_tags/', defaults={'qid' : None}, methods=['GET', 'POST'])
def get_tags(qid=None):
    if qid is not None:
        question = qb.get(str(qid)).value

        tags = question['content']['tags']

        tags_list = []
        tids_list = []
        for i in tags:
            #print i
            tag = urllib2.urlopen(DB_URL + 'tags/_design/dev_qa/_view/get_doc_from_tag?key=' + '"' + str(i) + '"').read()
            tag = json.loads(tag)['rows'][0]['id']
            tids_list.append(tag)

        if len(tids_list) != 0:
            val_res = tb.get_multi(tids_list)
        tags = []
        for tid in tids_list:
            tags_list.append({"id": val_res[str(tid)].value['tid'], "name": val_res[str(tid)].value['tag']})
        return json.dumps(tags_list)
    else:
        query = request.args.get('q')
        #print query
        if query is not None:
            q=pyes.MatchQuery('tag', query)
            tags_result=es_conn.search(query=q)
            results=[]

            for r in tags_result:
                results.append({'id': str(r['tid']), 'name':r['tag']})

            return json.dumps(results)

def add_tags(tags_passed, qid):
    for tag in tags_passed:
        try:
            document = tb.get(tag).value
            document['count'] += 1
            #document['qid'].append(qid)
            tb.replace(tag.lower(), document)

        except:
            data = {}
            data['qid'] = []
            data['excerpt'] = ""
            data['tag'] = tag
            data['count'] = 1
            data['info'] = ""
            #data['qid'].append(qid)

            tid = tb.incr('tcount', 1).value
            data['tid'] = tid

            tb.add(tag, data)
            es_conn.index({'tag':tag, 'tid':tid, 'position':tid}, 'tags', 'tags-type', tid)
            es_conn.indices.refresh('tags')


def replace_tags(tags_passed, qid, current_tags):
    for tag in tags_passed:
        if tag not in current_tags:
	    tid = 0
            try:
                document = tb.get(tag).value
                document['count'] += 1
                #document['qid'].append(qid)
                tb.replace(tag, document)

            except:
                data = {}
                data['qid'] = []
                data['excerpt'] = ""
                data['tag'] = tag
                data['count'] = 1
                data['info'] = ""
                #data['qid'].append(qid)

                tid = tb.incr('tcount', 1).value
                data['tid'] = tid

                tb.add(tag, data)
                es_conn.index({'tag':tag, 'tid':tid, 'position':tid}, 'tags', 'tags-type', tid)
                es_conn.indices.refresh('tags')

    for tag in current_tags:
        if tag not in tags_passed:
            print tag
            tag = urllib2.urlopen(DB_URL + 'tags/_design/dev_qa/_view/get_doc_from_tag?key=' + '"' + urllib2.quote(str(tag)) + '"').read()
            tid = json.loads(tag)['rows'][0]['id']
            tag = tb.get(tid).value
            #tag['qid'].remove(int(qid))
            tag['count'] -= 1

            tb.replace(tag['tag'], tag)
            if tag['count'] == 0:
                tb.delete(tag['tag'])
                tb.decr('tcount')

@kunjika.route('/vote_clicked', methods=['GET', 'POST'])
def vote_clicked():
    return votes.handle_vote(request)


@kunjika.route('/edit/<element>', methods=['GET', 'POST'])
def edits(element):
    (qcount, acount, tcount, ucount, tag_list) = utility.common_data()
    #edit_list = edit.handle_edit(element)
    #p##print(edit_list)

    aid = 0
    cid = 0
    qid = 0

    edit_list = element.split('-')

    question = qb.get(edit_list[1]).value
    type = edit_list[0]
    form = ""
    qid = edit_list[1]
    if type == 'ce':
        form = CommentForm(request.form)
        if len(edit_list) == 3:
            cid = edit_list[2]
        else:
            cid = edit_list[3]
            aid = edit_list[2]
    elif type == 'ae':
        form = AnswerForm(request.form)
        aid = edit_list[2]
    elif type == 'qe':
        form = QuestionForm(request.form)

    if request.method == 'POST':
        if 'version' not in question:
            question['version'] = 1
            question['type'] = 'qb' # question backup
            question['editor'] = g.user.id
        else:
            question['version'] += 1

        if type == 'ce':
            if form.validate_on_submit():
                if aid != 0:
                    question['answers'][int(aid) - 1]['comments'][int(cid) - 1]['comment'] = form.comment.data
                else:
                    question['comments'][int(cid) - 1]['comment'] = form.comment.data

                editor = cb.get(str(g.user.id)).value
                editor['rep'] += 1
                question['updated'] = int(time())
                qb.replace(qid, question)

                kb.add(edit_list[1] + '_v' + str(question['version']), question)

            return redirect(url_for('questions', qid=int(qid), url=utility.generate_url(question['title'])))
        elif type == 'ae':
            if form.validate_on_submit():
                question['answers'][int(aid) - 1]['answer'] = form.answer.data

                editor = cb.get(str(g.user.id)).value
                editor['rep'] += 1
                question['updated'] = int(time())
                qb.replace(qid, question)

                kb.add(edit_list[1] + '_v' + str(question['version']), question)

            return redirect(url_for('questions', qid=int(qid), url=utility.generate_url(question['title'])))
        else:
            if form.validate_on_submit():
                question['content']['description'] = form.description.data
                # title editing disabled so that existing links do not break
                #title = form.question.data
                #url = utility.generate_url(title)
                #question['content']['url'] = url
                #question['title'] = title
                tags = form.tags.data.split(',')
                tags = [tag.strip(' \t').lower() for tag in tags]
                tag_list = []
                #question['content']['tags'] = [tag.strip(' \t').lower() for tag in question['content']['tags']]
                current_tags = question['content']['tags']
                new_tag_list = []
                for tag in tags:
                    tag = list(tag)
                    for i in range(0, len(tag)):
                        if tag[i] == '`' or tag[i] == '~' or tag[i] == '!' or tag[i] == '@' or tag[i] == '#' \
                             or tag[i] == '$' or tag[i] == '%' or tag[i] == '^' or tag[i] == '&' or tag[i] == '+' \
                             or tag[i] == '+'  or tag[i] ==  '{' or tag[i] == '[' or tag[i] == ']' or tag[i] == '}' \
                             or tag[i] == '\\' or tag[i] == '|' or tag[i] == ':' or tag[i] == ';' or tag[i] == '\''\
                             or tag[i] == '<' or tag[i] == '>' or tag[i] == ',' or tag[i] == '?' or tag[i] == '/'\
                             or tag[i] == ' ':
                            tag[i] = '-'
                    tag_list.append(''.join(tag))

                for tag in tag_list:
                    try:
                        #tag = int(tag)
                        tag = urllib2.urlopen(DB_URL + 'tags/_design/dev_qa/_view/get_tag_by_id?stale=false&key=' + str(tag)).read()
                        tid = json.loads(tag)['rows'][0]['id']
                        tag = tb.get(str(tid)).value
                        new_tag_list.append(tag['tag'])

                    except:
                        ##print "hello"
                        new_tag_list.append(tag)

                question['updated'] = int(time())
                question['content']['tags'] = new_tag_list
                editor = cb.get(str(g.user.id)).value
                editor['rep'] += 1
                qb.replace(str(qid), question)

                kb.add(edit_list[1] + '_v' + str(question['version']), question)
                es_conn.index({'title':question['title'], 'description':question['content']['description'], 'qid':question['qid'],
                               'position':question['qid']}, 'questions', 'questions-type', question['qid'])
                es_conn.indices.refresh('questions')

                replace_tags(question['content']['tags'], question['qid'], current_tags)
            return redirect(url_for('questions', qid=int(qid), url=utility.generate_url(question['title'])))
    else:
        return render_template('edit.html', title='Edit', form=form, question=question, type=type, qid=qid,
                               aid=int(aid), cid=int(cid), qcount=qcount, ucount=ucount, tcount=tcount,
                               acount=acount, tag_list=tag_list, name=g.user.name, role=g.user.role, user_id=g.user.id)


@kunjika.route('/answer_accepted')
def answer_accepted():
    return utility.accept_answer(request.args.get('id'))


@kunjika.route('/favorited')
def favorited():
    return utility.handle_favorite(request.args.get('id'))

@kunjika.route('/flag')
def flag():
    idntfr = request.args.get('id')
    url = request.args.get('url')
    user = cb.get(str(g.user.id)).value
    idntfr_list = idntfr.split('-')

    question = qb.get(str(idntfr_list[1])).value
    op_id = 0
    ##print idntfr_list
    if idntfr_list[0] == '#qqf':
        op_id = question['content']['op']
    elif idntfr_list[0] == '#qcf':
        for comment in question['comments']:
            if unicode(comment['cid']) == idntfr_list[1]:
                op_id = comment['poster']
    elif idntfr_list[0] == '#qaf':
        for answer in question['answers']:
            if unicode(answer['aid']) == idntfr_list[2]:
                op_id = answer['poster']
    elif idntfr_list[0] == unicode('#qac'):
        for answer in question['answers']:
            ##print "hello"
            if unicode(answer['aid']) == idntfr_list[2]:
                for comment in answer['comments']:
                    if unicode(comment['cid']) == idntfr_list[3]:
                        op_id = comment['poster']
                        ##print op_id

    ##print op_id

    flagged_user = cb.get(str(op_id)).value

    msg = Message("Inappropriate content flag for element " + str(idntfr))
    msg.recipients = [admin]
    msg.sender = admin
    msg.html = '<p>Hi,<br/><br/>' \
               'URL: ' + url + '<br/><br/>' \
               'Flagger Name: ' + str(user['name']) + '<br/>' \
               'Flagger Email: ' + str(user['email']) + '<br/>' \
               'Flagger ID: ' + str(user['id']) + '<br/><br/>' \
               'Flagged User Name: ' + str(flagged_user['name']) + '<br/>' \
               'Flagger User Email: ' + str(flagged_user['email']) + '<br/>' \
               'Flagger User ID: ' + str(flagged_user['id']) + '<br/>' \
               '<br/> Admin<p>'
    mail.send(msg)

    return jsonify({"success": True})

@kunjika.route('/postcomment', methods=['GET', 'POST'])
def postcomment():
    ###print request.form
    ###print type(request.form['comment'])
    #user = cb.get(str(g.user.id)).value
    user = g.user.user_doc

    if len(request.form['comment']) < 10 or len(request.form['comment']) > 5000:
        return "Comment must be between 10 and 5000 characters."
    else:
        elements = request.form['element'].split('-')
        qid = elements[0]
        ###print "qid = " + qid
        aid = 0
        if len(elements) == 2: # check if comment has been made on answers
            aid = elements[1]
            ###print "aid = ",  aid   # if it is on question aid will be zero

    question = qb.get(qid).value
    aid = int(aid)
    comment = {}
    #comment['aid'] = questions_dict['acount'] + 1
    comment['comment'] = request.form['comment']
    comment['poster'] = g.user.id
    comment['opname'] = g.user.name
    comment['ts'] = int(time())
    comment['ip'] = request.remote_addr
    if aid != 0:
        aid -= 1
        if 'comments' in question['answers'][aid]:
            question['answers'][aid]['ccount'] += 1
            comment['cid'] = question['answers'][aid]['ccount']
            question['answers'][aid]['comments'].append(comment)
        else:
            question['answers'][aid]['ccount'] = 1
            question['answers'][aid]['comments'] = []
            comment['cid'] = 1
            question['answers'][aid]['comments'].append(comment)
    else:
        if 'comments' in question:
            question['ccount'] += 1
            comment['cid'] = question['ccount']
            question['comments'].append(comment)
        else:
            question['ccount'] = 1
            question['comments'] = []
            comment['cid'] = 1
            question['comments'].append(comment)

    #p##print(question)
    question['updated'] = int(time())
    qb.replace(str(qid), question)
    email_list = []
    email_list.append(str(question['content']['op']))
    if 'comments' in question:
        for comment in question['comments']:
            email_list.append(str(comment['poster']))
    if 'answers' in question:
        for answer in question['answers']:
            email_list.append(str(answer['poster']))
            if 'comments' in answer:
                for comment in question['comments']:
                    email_list.append(str(comment['poster']))

    email_list = set(email_list)
    current_user_list = [str(g.user.id)]
    email_list = email_list - set(current_user_list)
    email_list = list(email_list)

    if len(email_list) != 0:
        email_users = cb.get_multi(email_list)
        email_list = []

        for id in email_users:
            email_list.append(email_users[str(id)].value['email'])

        #print email_list

        msg = Message("A new answer has been posted to a question where you have answered or commented")
        msg.recipients = email_list
        msg.sender = admin
        msg.html = "<p>Hi,<br/><br/> A new comment has been posted which you can read at " +\
        HOST_URL + "questions/" + str(question['qid']) + '/' + question['content']['url'] + \
        " <br/><br/>Best regards,<br/>Kunjika Team<p>"
        mail.send(msg)

    ts = strftime("%a, %d %b %Y %H:%M", localtime(comment['ts']))
    #return '<div class="comment" id="c-' + str(comment['cid']) + '">' + request.form['comment'] +'<div>&mdash;</div>' \
    #       '<a href="/users/"' + str(g.user.id) + '/' + g.user.name + '>' + g.user.name +'</a> ' + str(ts) +'</div>'
    return json.dumps({"id": comment['cid'], "comment": request.form['comment'], "user_id": g.user.id,
                       "uname": g.user.name, "ts": ts})


@kunjika.route('/unanswered', defaults={'page': 1})
@kunjika.route('/unanswered/page/<int:page>')
def unanswered(page):
    (qcount, acount, tcount, ucount, tag_list) = utility.common_data()
    skip = (page - 1) * QUESTIONS_PER_PAGE

    q = Query(descending=True, limit=50)
    questions_list = []
    count = 0
    for result in View(qb, "dev_qa", "get_unanswered", include_docs=True, query=q):
        ##print result
        questions_list.append(result.doc.value)
        count += 1

    for i in questions_list:
        i['tstamp'] = strftime("%a, %d %b %Y %H:%M", localtime(float(i['content']['ts'])))

        user = cb.get(i['content']['op']).value
        i['opname'] = user['name']

    if not questions_list and page != 1:
        abort(404)
    pagination = utility.Pagination(page, QUESTIONS_PER_PAGE, count)
    if g.user is None:
        return render_template('unanswered.html', title='Unanswered questions', unpage=True, questions=questions_list,
                               pagination=pagination, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)
    elif g.user is not None and g.user.is_authenticated():
        return render_template('unanswered.html', title='Unanswered questions', unpage=True, questions=questions_list,
                               name=g.user.name, role=g.user.role, user_id=g.user.id, pagination=pagination,
                               qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)
    else:
        return render_template('unanswered.html', title='Unanswered questions', unpage=True, questions=questions_list,
                               pagination=pagination, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)


@kunjika.route('/users/', defaults={'page': 1})
@kunjika.route('/users/page/<int:page>')
def show_users(page):
    (qcount, acount, tcount, ucount, tag_list) = utility.common_data()
    count = cb.get('count').value
    users = utility.get_users_per_page(page, USERS_PER_PAGE, count)
    if not users and page != 1:
        abort(404)
    pagination = utility.Pagination(page, USERS_PER_PAGE, count)
    no_of_users = len(users)
    if g.user is not None and g.user.is_authenticated():
        logged_in = True
        return render_template('users.html', title='Users', gravatar32=gravatar32, logged_in=logged_in, upage=True,
                               pagination=pagination, users=users, no_of_users=no_of_users,
                               qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list,
                               name=g.user.name, role=g.user.role, user_id=g.user.id)
    return render_template('users.html', title='Users', gravatar32=gravatar32, upage=True,
                           pagination=pagination, users=users, no_of_users=no_of_users, name=g.user.name,
                           qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)


@kunjika.route('/tags/', defaults={'page': 1})
@kunjika.route('/tags/page/<int:page>')
def show_tags(page):
    tag_list = []
    qcount = qb.get('qcount').value
    ucount = cb.get('count').value
    tcount = tb.get('tcount').value
    acount = urllib2.urlopen(DB_URL + 'questions/_design/dev_qa/_view/get_acount?reduce=true').read()
    acount = json.loads(acount)
    if len(acount['rows']) is not 0:
        acount = acount['rows'][0]['value']
    else:
        acount = 0
    if tcount > 0:
        tag_list = utility.get_popular_tags()
    count = tb.get('tcount').value
    tags = utility.get_tags_per_page(page, TAGS_PER_PAGE, count)
    if not tags and page != 1:
        abort(404)
    pagination = utility.Pagination(page, TAGS_PER_PAGE, count)
    no_of_tags = len(tags)
    if g.user is not None and g.user.is_authenticated():
        logged_in = True
        return render_template('tags.html', title='Tags', logged_in=logged_in, tpage=True, pagination=pagination,
                               tags=tags, no_of_tags=no_of_tags, qcount=qcount, ucount=ucount, tcount=tcount,
                               name=g.user.name, role=g.user.role, user_id=g.user.id, acount=acount, tag_list=tag_list)
    return render_template('tags.html', title='Tags', tpage=True, pagination=pagination, tags=tags,
                           no_of_tags=no_of_tags, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)

def make_external(url):
    return urljoin(request.url_root, url)

@kunjika.route('/recent-questions.atom')
def recent_feed():
    feed = AtomFeed('Recent Questions',
                    feed_url=request.url, url=request.url_root)

    q = Query(descending=True, limit=50)
    question_list = []
    for result in View(qb, "dev_qa", "get_questions", include_docs=True, query=q):
        question_list.append(result.doc.value)

    for question in question_list:
        feed.add(question['title'], unicode(question['content']['description']),
             content_type='html',
             author=HOST_URL + 'users/' + unicode(question['content']['op']) + question['opname'],
             url=make_external(HOST_URL + 'questions' + '/' + unicode(question['qid']) + "/" + question['content']['url']),
             updated=datetime.fromtimestamp(question['updated']))
    return feed.get_response()

@kunjika.route('/ban')
def ban():
    #just allow admin this
    if g.user.id == 1:
        user_id = request.args.get('id')

        #user = cb.get(str(user_id)).value
        user = g.user.user_doc
        if user['banned'] is False:
            user['banned'] = True
        else:
            user['banned'] = False

        cb.replace(user_id, user)

        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

@kunjika.route('/info', methods=['GET', 'POST'])
@kunjika.route('/info/<string:tag>')
def tag_info(tag=None):
    if tag is None:
        tag = request.args.get('tag')
    tag_list = []
    (qcount, acount, tcount, ucount, tag_list) = utility.common_data()
    tag = urllib2.urlopen(DB_URL + 'tags/_design/dev_qa/_view/get_doc_from_tag?key=' + '"' + urllib2.quote(str(tag)) + '"').read()
    tid = json.loads(tag)['rows'][0]['id']
    tag = tb.get(tid).value
    if g.user is AnonymousUserMixin:
        return render_template('tag_info.html', title='Info', tag=tag, tpage=True)
    elif g.user is not None and g.user.is_authenticated():
        return render_template('tag_info.html', title='Info', tag=tag, tpage=True)
    else:
        return render_template('tag_info.html', title='Info', tag=tag, tpage=True)

@kunjika.route('/edit_tag/<string:tag>', methods=['POST'])
def edit_tag(tag):
    (qcount, acount, tcount, ucount, tag_list) = utility.common_data()

    tag = urllib2.urlopen(DB_URL + 'tags/_design/dev_qa/_view/get_doc_from_tag?key=' + '"' + urllib2.quote(tag) + '"').read()
    tid = json.loads(tag)['rows'][0]['id']
    tag = tb.get(tid).value
    tagForm = TagForm(request.form)
    if g.user is not None and g.user.is_authenticated():
        if tagForm.validate_on_submit() and request.method == 'POST':
            tag['info'] = tagForm.info.data
            ##print "hello"
            tb.replace(tag['tag'], tag)
            return redirect(url_for('tag_info', tag=str(tag['tag'])))

        return render_template('edit_tag.html', title='Edit tag', form=tagForm, tpage=True, name=g.user.name, role=g.user.role, tag=tag,
                               user_id=g.user.id, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)
    return redirect(url_for('login'))

@kunjika.route('/reset_password', methods=['GET', 'POST'])
@kunjika.route('/reset_password/<string:token>', methods=['GET', 'POST'])
def reset_password(token=None):
    s = TimestampSigner(kunjika.config['SECRET_KEY'])
    if token is None:
        emailForm = EmailForm(request.form)
        if emailForm.validate_on_submit() and request.method == 'POST':
            email = emailForm.email.data
            document = urllib2.urlopen(
                DB_URL + 'default/_design/dev_qa/_view/get_id_from_email?key=' + '"' + urllib2.quote(email) + '"&stale=false').read()
            document = json.loads(document)
            if len(document['rows']) != 0:
                if 'id' in document['rows'][0]:
                    document = cb.get(document['rows'][0]['id']).value
                if document['email'] == email and 'password' in document:
                    token = s.sign(email)
                    msg = Message("Password reset")
                    msg.recipients = [email]
                    msg.sender = admin
                    msg.html = "<p>Hi,<br/>A password reset request has been initiated " \
                               "by you. You can reset your password at " \
                               "<a href=" + HOST_URL + "reset_password/" + token + ">" + HOST_URL + "reset_password/" + token + "</a>." \
                               "However, if you have not raised this request no need to change " \
                               "your password just send an email to " + admin + ". Note that this " \
                               "token is only valid for 1 day. <br/>Best regards," \
                               "<br/> Admin</p>"
                    ##print type(token)
                    ##print type(email)
                    mail.send(msg)
                else:
                    flash('You seem to have openid login, your password cannot be reset here.', 'error')
                    return redirect(url_for('login'))
            else:
                flash('The email was not found in database.', 'error')
                return redirect(url_for('reset_password'))
        return render_template('reset_password.html', emailForm=emailForm, title="Reset Password")
    elif token is not None:
        passwordResetForm = PasswordResetForm(request.form)
        if passwordResetForm.validate_on_submit() and request.method == 'POST':
            try:
                email = s.unsign(token, max_age=86400)

                document = urllib2.urlopen(
                    DB_URL + 'default/_design/dev_qa/_view/get_id_from_email?key=' + '"' + urllib2.quote(email) + '"&stale=false').read()
                document = json.loads(document)
                if 'id' in document['rows'][0]:
                    try:
                        document = cb.get(str(document['rows'][0]['id'])).value
                    except:
                        return redirect(url_for('questions'))
                    passwd_hash = bcrypt.generate_password_hash(passwordResetForm.password.data)
                    document['password'] = passwd_hash
                    cb.replace(str(document['id']), document)
            except:
                #print "Either signature is bad or token has expired"
                return redirect(url_for('questions'))

            return redirect(url_for('questions'))
        return render_template('reset_password.html', passwordResetForm=passwordResetForm, token=token, title="Reset Password")
    else:
        return redirect(url_for('questions'))

@kunjika.route('/editing-help')
def editing_help():
    return render_template('editing-help.html', title='Markdown Editor Help', name=g.user.name,
                           user_id=g.user.id)

@kunjika.route('/search-help')
def search_help():
    (qcount, acount, tcount, ucount, tag_list) = utility.common_data()
    if g.user is not None and g.user.is_authenticated():
        #user = cb.get(str(g.user.id)).value
        user = g.user.user_doc
        return render_template('search-help.html', title='Search help', tpage=True, name=g.user.name,
                               user_id=g.user.id, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)
    return render_template('search-help.html', title='Search help', tpage=True, name=g.user.name,
                               user_id=g.user.id, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)

@kunjika.route('/sticky')
def stikcy():
    if g.user.id == 1:
        qid=request.args.get('id')[2:]
        ##print qid
        question = qb.get(str(qid)).value
        if 'sticky' not in question:
            question['sticky'] = True
        elif question['sticky'] is False:
            question['sticky'] = True
        else:
            question['sticky'] = False

        qb.replace(str(qid), question)
        ##print "questions stickied"

        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

@kunjika.route('/close')
def close():
    if g.user.id == 1:
        qid=request.args.get('id')[2:]
        ##print qid
        question = qb.get(str(qid)).value
        if question['close'] == False:
            question['close'] = True
        elif question['close'] == True:
            question['close'] = False

        qb.replace(str(qid), question)
        ##print "questions stickied"

        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

@kunjika.route('/poll', methods=['GET', 'POST'])
def poll():
    (qcount, acount, tcount, ucount, tag_list) = utility.common_data()

    pollForm = PollForm(request.form)

    class ChoiceForm(Form):
        tags = TextField('Tags', [validators.Length(min=1, max=100), validators.Required()])
        question = TextField('Question', [validators.Length(min=4, max=200), validators.Required()])
        option = RadioField('What type of poll do you want?', choices=[('Single choice', 'Single Choice'), ('Multiple choice', 'Multiple choice')])
        description = TextAreaField('', [validators.Length(min=20, max=5000), validators.Required()])
        option_1 = TextField('Question', [validators.Length(min=4, max=200), validators.Required()])
        option_2 = TextField('Question', [validators.Length(min=4, max=200), validators.Required()])
        option_3 = TextField('Question', [validators.Length(min=4, max=200), validators.Optional()])
        option_4 = TextField('Question', [validators.Length(min=4, max=200), validators.Optional()])
        option_5 = TextField('Question', [validators.Length(min=4, max=200), validators.Optional()])
        option_6 = TextField('Question', [validators.Length(min=4, max=200), validators.Optional()])
        option_7 = TextField('Question', [validators.Length(min=4, max=200), validators.Optional()])
        option_8 = TextField('Question', [validators.Length(min=4, max=200), validators.Optional()])
        option_9 = TextField('Question', [validators.Length(min=4, max=200), validators.Optional()])
        option_10 = TextField('Question', [validators.Length(min=4, max=200), validators.Optional()])

    questionForm = ChoiceForm(request.form)

    choices = []

    if g.user is not None and g.user.is_authenticated():
        #user = cb.get(str(g.user.id)).value
        user = g.user.user_doc
        if pollForm.validate_on_submit() and request.method == 'POST':
            for i in range(0, int(pollForm.poll_answers.data)):
                choices.append(str(i+1))

            return render_template('create_poll.html', title='Create Poll', form=questionForm, options=choices, ppage=True, name=g.user.name, role=g.user.role,
                       user_id=g.user.id, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)

        if questionForm.validate_on_submit() and request.method == 'POST':

            title =  questionForm.question.data
            option =  questionForm.option.data
            option_1 =  questionForm.option_1.data
            option_2 =  questionForm.option_2.data

            question = {}
            question['content'] = {}
            question['content']['description'] = questionForm.description.data
            question['content']['tags'] = []
            question['content']['tags'] = questionForm.tags.data.split(',')
            question['title'] = title

            if option == 'Single choice':
                question['content']['sc'] = True
            else:
                question['content']['mc'] = True

            question['content']['options'] = []
            question['content']['options'].append(option_1)
            question['content']['options'].append(option_2)

            if questionForm.option_3.data != "":
                question['content']['options'].append(questionForm.option_3.data)
                if questionForm.option_4.data != "":
                    question['content']['options'].append(questionForm.option_4.data)
                    if questionForm.option_5.data != "":
                        question['content']['options'].append(questionForm.option_5.data)
                        if questionForm.option_6.data != "":
                            question['content']['options'].append(questionForm.option_6.data)
                            if questionForm.option_7.data != "":
                                question['content']['options'].append(questionForm.option_7.data)
                                if questionForm.option_8.data != "":
                                    question['content']['options'].append(questionForm.option_8.data)
                                    if questionForm.option_9.data != "":
                                        question['content']['options'].append(questionForm.option_9.data)
                                        if questionForm.option_10.data != "":
                                            question['content']['options'].append(questionForm.option_10.data)

            url = utility.generate_url(title)

            question['content']['url'] = url
            question['content']['op'] = str(g.user.id)
            question['content']['ts'] = int(time())
            question['updated'] = question['content']['ts']
            question['content']['ip'] = request.remote_addr

            question['qid'] = qb.incr('qcount', 1).value
            question['votes'] = 0
            question['acount'] = 0
            question['views'] = 0
            question['votes_list'] = []

            #user = cb.get(str(g.user.id)).value
            user = g.user.user_doc

            user['rep'] += 1
            user['qcount'] += 1

            qb.add(str(question['qid']), question)

            cb.replace(str(g.user.id), user)

            add_tags(question['content']['tags'], question['qid'])

            return redirect(url_for('questions', qid=question['qid'], url=question['content']['url']))

        return render_template('poll.html', title='Poll', form=pollForm, ppage=True, name=g.user.name, role=g.user.role,
                               user_id=g.user.id, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)
    return redirect(url_for('login'))

@kunjika.route('/search', defaults={'page': 1})
@kunjika.route('/search/<int:page>')
def search(page=None):
    query=request.args.get('query')
    if query[0:6]=='title:':
        return utility.search_title(query, page)
    elif query[0:12]=='description:':
        return utility.search_description(query, page)
    elif query[0:5]=='user:':
        return utility.search_user(query, page)
    elif query[0:4]=='tag:':
        return utility.search_tag(query, page)
    else:
        return utility.search(query, page)

@kunjika.route('/get_autocomplete', methods=['GET', 'POST'])
def get_autocomplete():
    return utility.get_autocomplete(request)


@kunjika.route('/send_invites', methods=['GET', 'POST'])
def send_invites():
    res = utility.send_invites(request)
    #not needed user = cb.get(str(g.user.id)).value
    if res is True:
        flash('Your invites were successfully sent.', 'success')
    else:
        flash('Your invites could not be sent.', 'error')
    return redirect(url_for('users', uid=str(g.user.id)))


@kunjika.route('/administration', methods=['GET', 'POST'])
def administration():
    (qcount, acount, tcount, ucount, tag_list) = utility.common_data()
    form = BulkEmailForm(request.form)
    #user = cb.get(str(g.user.id)).value
    try:
        user = g.user.user_doc
    except:
        return redirect(url_for('login'))
    #print request.method

    if g.user.id == 1:
        if request.method == 'POST' and form.validate_on_submit():
            document = urllib2.urlopen(DB_URL + 'default/_design/dev_qa/_view/get_id_from_email').read()
            document = json.loads(document)
            email_list = []
            for row in document['rows']:
                each_doc = cb.get(row['id']).value
                if each_doc['receive-email'] is True:
                    email_list.append(row['value']['email'])
            ##print document
            msg = Message(form.subject.data)
            msg.recipients = email_list
            msg.sender = (',').join(email_list)
            msg.html = form.bulk_mail.data
            try:
                mail.send(msg)
                #print msg
                flash('Email sent to all users.', 'success')
            except:
                flash('Email could not be sent.', 'error')
            return redirect(url_for('users', uid=g.user.id))
        return render_template('admin.html', form=form, user=user, name=g.user.name, role=g.user.role, adpage=True,
                               user_id=g.user.id, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)
    else:
        flash('You need to be admin to view this page', 'Error')
        return redirect(url_for('questions'))


@kunjika.route('/users/<uid>/edit_profile', methods=['GET', 'POST'])
def edit_profile(uid=None):
    (qcount, acount, tcount, ucount, tag_list) = utility.common_data()
    form = EditProfileForm(request.form)
    #user = cb.get(str(g.user.id)).value
    user = g.user.user_doc

    if (g.user.id == user['id']):
        if request.method == 'POST' and form.validate_on_submit() :
            user['fname'] = form.fname.data
            user['lname'] = form.lname.data
            user['website'] = form.website.data
            user['location'] = form.location.data
            user['about-me'] = form.about_me.data
            #print form.skills.data
            skills = form.skills.data.split(',')
            current_skills = []
            if 'skills' in user:
                current_skills = user['skills']
            user['skills'] = []
            if len(skills) != 0:
                for skill in skills:
                    if skill.isdecimal():
                        user['skills'].append(current_skills[int(skill)])
                    else:
                        user['skills'].append(skill)
            user['skills'].sort()
            cb.replace(str(g.user.id), user)

            return redirect(url_for('users', uid=g.user.id, uname=g.user.name))
        return render_template('edit_profile.html', title='Edit Profile', form=form, user=user, name=g.user.name, role=g.user.role,
                               user_id=g.user.id, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)

    return redirect(url_for('users', uid=g.user.id, name=g.user.name ))


@kunjika.route('/users/<uid>/<uname>/settings', methods=['GET', 'POST'])
def settings(uid=None, uname=None):
    (qcount, acount, tcount, ucount, tag_list) = utility.common_data()
    form = PasswordResetForm(request.form)

    #user = cb.get(str(g.user.id)).value
    user = g.user.user_doc

    if (g.user.id == user['id']):
        if request.method == 'POST' and form.validate_on_submit() :
            passwd = request.form['password']
            confirm = request.form['confirm']

            if passwd == confirm:
                passwd_hash = bcrypt.generate_password_hash(passwd)
                user['password'] = passwd_hash
                try:
                    cb.replace(str(g.user.id), user)
                    flash('Your password was successfuly chnaged.', 'success')
                except:
                    flash('Your password could not be changed. Contact admin', 'error')
            else:
                return render_template('settings.html', form=form, user=user, name=g.user.name, role=g.user.role,
                                       user_id=g.user.id, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)
            return redirect(url_for('users', uid=g.user.id, uname=user['name']))
        return render_template('settings.html', form=form, user=user, name=g.user.name, role=g.user.role,
                               user_id=g.user.id, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)

    return redirect(url_for('users', uid=g.user.id ))


@kunjika.route('/notify')
def notify():
    notify = request.args.get('#id')
    #user = cb.get(str(g.user.id)).value
    user = g.user.user_doc

    if user['receive-emails'] is False:
        user['receive-emails'] = True
        response = {'success': 'true'}
    else:
        user['receive-emails'] = False
        response = {'success': 'false'}

    try:
        cb.replace(str(g.user.id), user)

        return jsonify(response)
    except:
        return jsonify(response)

@kunjika.route('/bookmark')
def bookmark():
    qid = request.args.get('id')
    print qid.split('-')[1]
    bookmark = qb.get(qid.split('-')[1]).value
    #print bookmark
    bid = 'bq-' + qid.split('-')[1] + '-' + str(g.user.id) # bq stands for bookmark question

    try:
        bookmark_doc = kb.get(bid).value
        if bookmark_doc['status'] == False:
            bookmark_doc['status'] = True
            kb.replace(bid, bookmark_doc)
            return jsonify({'bookmark': True})
        else:
            bookmark_doc['status'] = False
            kb.replace(bid, bookmark_doc)
            return jsonify({'bookmark': False})
    except:
        bookmark_doc = {}
        bookmark_doc['id'] = bid
        bookmark_doc['_type'] = 'bq' # bq stands for bookmark question
        bookmark_doc['title'] = bookmark['title']
        bookmark_doc['qid'] = bookmark['qid']
        bookmark_doc['tags'] = bookmark['content']['tags']
        bookmark_doc['uid'] = g.user.id
        bookmark_doc['name'] = g.user.name
        bookmark_doc['status'] = True
        kb.add(bid, bookmark_doc)
        return jsonify({'bookmark': True})

@kunjika.route('/users/<uid>/<name>/bookmarks', defaults={'page': 1})
@kunjika.route('/users/<uid>/<name>/bookmarks/<int:page>')
def user_bookmarks(uid, name, page=1):
    if int(uid) != g.user.id:
        flash('You are not allowed to view the bookmarks other than your own.', 'error')
        return redirect(request.referrer)
    skip = (page - 1) * QUESTIONS_PER_PAGE
    questions = urllib2.urlopen(DB_URL + 'kunjika/_design/dev_qa/_view/get_bookmarks_by_uid?limit=' +
                                str(QUESTIONS_PER_PAGE) + '&skip=' + str(skip) + '&key=' +
                                str(uid) + '&reduce=false').read()
    #print questions
    count = urllib2.urlopen(DB_URL + 'kunjika/_design/dev_qa/_view/get_bookmarks_by_uid?key=' +
                            str(uid)).read()
    count = json.loads(count)['rows']
    if len(count) != 0:
        count = count[0]['value']
    else:
        count = 0
    #print count
    questions = json.loads(questions)
    qids = []
    if len(questions) > 0:
        for row in questions['rows']:
            qids.append((str(row['id'])).split('-')[1])

    print qids
    if len(qids) != 0:
        val_res = qb.get_multi(qids)
    questions_list = []
    for qid in qids:
        questions_list.append(val_res[str(qid)].value)

    #count = len(questions_list)
    if not questions_list and page != 1:
        abort(404)
    pagination = utility.Pagination(page, QUESTIONS_PER_PAGE, int(count))
    gravatar100 = Gravatar(kunjika,
                           size=100,
                           rating='g',
                           default='identicon',
                           force_default=False,
                           force_lower=False)
    try:
        user = cb.get(str(g.user.id)).value
    except:
        pass

    logged_in = False
    if uid in session:
        logged_in = True
	if g.user.is_authenticated():
	        return render_template('bookmarks.html', title=user['name'], user_id=user['id'], name=user['name'], fname=user['fname'], \
        	                       lname=user['lname'], email=user['email'], gravatar=gravatar100, logged_in=logged_in, \
                	               role=g.user.role, bookmarks_pagination = pagination, user=user, questions=questions_list)

    return render_template('bookmarks.html', title=user['name'], user_id=user['id'], name=user['name'], fname=user['fname'], \
        	                       lname=user['lname'], email=user['email'], gravatar=gravatar100, logged_in=logged_in, \
                	               role=g.user.role, bookmarks_pagination = pagination, user=user, questions=questions_list)

@kunjika.route('/get_skills/<uid>', methods=['GET', 'POST'])
def get_skills(uid=None):
    if uid is not None:
        user = cb.get(str(uid)).value
        if 'skills' in user and len(user['skills']) > 0:
            skills = user['skills']
            sids = []
            skill_list = []
            for i in range(0, len(skills)):
                sids.append(i)

            skills_list = zip(sids, skills)
            for id, skill in skills_list:
                skill_list.append({"id": str(id), "name": skill})
            return json.dumps(skill_list)
        else:
            return json.dumps({})
    else:
        return json.dumps({})

@kunjika.route('/users/<uid>/<name>/skills')
def user_skills(uid, name):
    if not g.user.is_authenticated():
        flash('You need to be logged in to view skills and endorsements.', 'error')
        return redirect(request.referrer)
    user = cb.get(str(uid)).value
    gravatar100 = Gravatar(kunjika,
                           size=100,
                           rating='g',
                           default='identicon',
                           force_default=False,
                           force_lower=False)
    gravatar32 = Gravatar(kunjika,
                           size=32,
                           rating='g',
                           default='identicon',
                           force_default=False,
                           force_lower=False)
    logged_in = False
    if uid in session:
        logged_in = True
    skills = []
    sids = []
    if 'skills' in user:
        for skill in user['skills']:
            sid_doc = urllib2.urlopen(DB_URL + 'kunjika/_design/dev_qa/_view/get_end_by_uid?key=[' + str(user['id']) + \
                                       ',"' + urllib.quote(skill) + '"]&stale=false&reduce=false').read()
            sid_doc = json.loads(sid_doc)
            #print sid_doc
            for row in sid_doc['rows']:
                sids.append(row['id'])

            if len(sids) != 0:
                val_res = kb.get_multi(sids)

            endorsements = []
            has_endorsement = False
            for id in sids:
                endorsement = val_res[str(id)].value
                #endorser =  cb.get(str(val_res[str(id)].value['fuid']))
                #endorsement['email'] = endorser['email']
                #endorsement['fuid'] = endorser['id']
                endorsement['user'] = cb.get(str(endorsement['fuid'])).value
                endorsements.append(endorsement)
                #print endorsement
                if g.user.id == endorsement['fuid']:
                    has_endorsement = True

            sids = []
            count_doc = urllib2.urlopen(DB_URL + 'kunjika/_design/dev_qa/_view/get_end_by_uid?key=[' + str(user['id']) +
                                       ',"' + urllib.quote(skill) + '"]&stale=false&reduce=true').read()
            count_doc = json.loads(count_doc)
            #print count_doc
            if len(count_doc['rows']) != 0:
                count = count_doc['rows'][0]['value']
            else:
                count = 0
            ##print endorsements

            #print has_endorsement
            if has_endorsement == True:
                skills.append({'endorsements': endorsements, 'count': count, 'has_end': True, 'tech': skill})
            else:
                skills.append({'endorsements': endorsements, 'count': count, 'has_end': False, 'tech': skill})
        skills = sorted(skills, key=lambda k: k['count'], reverse=True)
        #print skills

    if g.user.is_authenticated():
        return render_template('skills.html', title=user['name'], user_id=user['id'], name=user['name'], fname=user['fname'], \
                               lname=user['lname'], email=user['email'], gravatar=gravatar100, logged_in=logged_in, \
                               role=g.user.role, user=user, skills = skills, gravatar32=gravatar32)


@kunjika.route('/endorse')
def endorse():
   return utility.endorse()

@kunjika.route('/write', methods=['GET', 'POST'])
def write_article():
    return utility.write_article()

@kunjika.route('/', defaults={'page': 1}, methods=['GET', 'POST'])
@kunjika.route('/articles', defaults={'page': 1}, methods=['GET', 'POST'])
@kunjika.route('/articles/<aid>', methods=['GET', 'POST'])
@kunjika.route('/articles/<aid>/<url>', methods=['GET', 'POST'])
@kunjika.route('/articles/page/<int:page>')
@kunjika.route('/articles/tagged/<string:tag>', defaults={'page': 1}, methods=['GET', 'POST'])
@kunjika.route('/articles/tagged/<string:tag>/page/<int:page>')
def browse_articles(page=None, aid=None, tag=None, url=None):
    return utility.browse_articles(page, aid, tag)

@kunjika.route('/article_comment', methods=['GET', 'POST'])
def article_comment():
    return utility.article_comment()

@kunjika.route('/edit_article/<element>', methods=['GET', 'POST'])
def edit_article(element):
    return utility.edit_article(element)

@kunjika.route('/article_tags', defaults={'page': 1})
@kunjika.route('/article_tags/page/<int:page>')
def article_tags(page=1):
    return utility.article_tags(page)

@kunjika.route('/save_draft', methods=['POST'])
def save_draft():
    return
    utility.save_draft()

@kunjika.route('/sitemap.xml')
def sitemap():
    sitemap = open('sitemap.xml', 'r')
    sitemap = sitemap.read()
    return sitemap

'''
@kunjika.route('/invites')
def invites():
    invites = request.args.get('#id')
    user = cb.get(str(g.user.id)).value

    if user['receive-invites'] is False:
        user['receive-invites'] = True
        response = {'success': 'true'}
    else:
        user['receive-invites'] = False
        response = {'success': 'false'}

    try:
        cb.replace(str(g.user.id), user)

        return jsonify(response)
    except:
        return jsonify(response)

@kunjika.route('/check_group_name', methods=['GET','POST'])
def check_group_name():
    group_name = request.args.get('val')

    try:
        document = urllib2.urlopen(
            DB_URL + 'sundries/_design/dev_qa/_view/get_doc_by_group_name?key=' + '"' + group_name +
            '"&stale=false&type=group&owner=' + str(g.user.id)).read()
        document = json.loads(document)
        if len(document['rows']) != 0:
            return jsonify({'success': 'false'})
        else:
            return jsonify({'success': 'true'})
    except:
        return jsonify({'success': 'true'})


@kunjika.route('/create_group', methods=['GET', 'POST'])
def create_group():
    res = utility.create_group(request)
    if res is True:
        flash('Your group was successfully created.', 'success')
    else:
        flash('Your group could not be created. Please contact admin with group name.', 'error')
    return redirect(url_for('users', uid=str(g.user.id)))


@kunjika.route('/users/<uid>/<uname>/groups', defaults={'page': 1})
@kunjika.route('/users/<uid>/<uname>/groups/page/<int:page>')
def show_groups(page, uid, uname):
    (qcount, acount, tcount, ucount, tag_list) = utility.common_data()
    document = urllib2.urlopen(DB_URL +
                               'sundries/_design/dev_qa/_view/get_doc_by_type?key="group-member"&reduce=false&member-id=' +
                               str(g.user.id)).read()
    document = json.loads(document)['rows']

    groups = utility.get_groups_per_page(page, GROUPS_PER_PAGE, document)
    if not groups and page != 1:
        abort(404)
    pagination = utility.Pagination(page, GROUPS_PER_PAGE, len(document))
    no_of_groups = len(document)
    if g.user is not None and g.user.is_authenticated() and uid==str(g.user.id):
        logged_in = True
        return render_template('groups.html', logged_in=logged_in, gpage=True, pagination=pagination,
                               groups=groups, no_of_groups=no_of_groups, qcount=qcount, ucount=ucount, tcount=tcount,
                               name=g.user.name, role=g.user.role, user_id=g.user.id, acount=acount, tag_list=tag_list)
    return redirect(url_for('users', uid=g.user.id))
'''

@kunjika.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@kunjika.errorhandler(410)
def page_not_found(e):
    return render_template('410.html'), 410


@kunjika.errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 410


#@kunjika.errorhandler(400)
#def page_not_found(e):
#    return render_template('400.html'), 400


@kunjika.errorhandler(401)
def page_not_found(e):
    return render_template('401.html'), 401


@kunjika.errorhandler(405)
def page_not_found(e):
    return render_template('405.html'), 405


@kunjika.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


@kunjika.errorhandler(502)
def page_not_found(e):
    return render_template('502.html'), 502


@kunjika.errorhandler(503)
def page_not_found(e):
    return render_template('503.html'), 503

kunjika.register_blueprint(test_series)

if __name__ == '__main__':
    kunjika.run()
