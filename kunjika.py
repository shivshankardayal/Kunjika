from flask import Flask, session, render_template, abort, redirect, url_for, flash, make_response, request, g, jsonify
import json
from forms import *
from flaskext.bcrypt import Bcrypt
from couchbase import Couchbase
from couchbase.exceptions import *
import urllib2
from pprint import pprint
from flaskext.gravatar import Gravatar
from werkzeug import secure_filename, SharedDataMiddleware
import os
from os.path import basename
from time import localtime, strftime, time
from flask.ext.login import (LoginManager, current_user, login_required,
                             login_user, logout_user, UserMixin, AnonymousUser,
                             confirm_login, fresh_login_required)
from models import User, Anonymous
import question
import votes
import edit
import utility

UPLOAD_FOLDER = '/home/shiv/Kunjika/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

kunjika = Flask(__name__)
kunjika.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
kunjika.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
kunjika.config.from_object('config')
kunjika.debug = True
kunjika.add_url_rule('/uploads/<filename>', 'uploaded_file',
                     build_only=True)
kunjika.wsgi_app = SharedDataMiddleware(kunjika.wsgi_app, {
    '/uploads': kunjika.config['UPLOAD_FOLDER']})

lm = LoginManager()
lm.init_app(kunjika)

cb = Couchbase.connect("default")
qb = Couchbase.connect("questions")
tb = Couchbase.connect("tags")

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


@kunjika.before_request
def before_request():
    g.user = current_user


def get_user(uid):
    try:
        user_from_db = cb.get(str(uid)).value
        return User(user_from_db['fname'], user_from_db['id'])
    except NotFoundError:
        return None


@lm.user_loader
def load_user(uid):
    #print id
    user = get_user(int(uid))
    return user


@kunjika.route('/', methods=['GET', 'POST'])
@kunjika.route('/questions', methods=['GET', 'POST'])
@kunjika.route('/questions/<qid>', methods=['GET', 'POST'])
@kunjika.route('/questions/<qid>/<url>', methods=['GET', 'POST'])
def questions(qid=None, url=None):
    questions_dict = {}
    if qid is None:
        questions_list = question.get_questions()
        if g.user is None:
            return render_template('questions.html', title='Questions', qpage=True, questions=questions_list)
        elif g.user is not None and g.user.is_authenticated():
            return render_template('questions.html', title='Questions', qpage=True, questions=questions_list,
                                   fname=g.user.name, user_id=g.user.id)
        else:
            return render_template('questions.html', title='Questions', qpage=True, questions=questions_list)
    else:
        questions_dict = question.get_question_by_id(qid, questions_dict)
        if request.referrer == "http://localhost:5000/questions":
            questions_dict['views'] += 1
        elif request.host_url != "http://localhost:5000/":
            questions_dict['views'] += 1
        if g.user is AnonymousUser:
            return render_template('single_question.html', title='Questions', qpage=True, questions=questions_dict)
        elif g.user is not None and g.user.is_authenticated():
            answerForm = AnswerForm(request.form)
            if answerForm.validate_on_submit() and request.method == 'POST':
                answer = {}
                if 'answers' in questions_dict:
                    answer['aid'] = questions_dict['acount'] + 1
                    answer['answer'] = answerForm.answer.data
                    answer['poster'] = g.user.id
                    answer['ts'] = int(time())
                    answer['votes'] = 0
                    answer['ip'] = request.remote_addr
                    answer['best'] = False
                    questions_dict['acount'] += 1

                    questions_dict['answers'].append(answer)

                else:
                    answer['aid'] = 1
                    answer['answer'] = answerForm.answer.data
                    answer['poster'] = g.user.id
                    answer['ts'] = int(time())
                    answer['votes'] = 0
                    answer['ip'] = request.remote_addr
                    answer['best'] = False
                    questions_dict['acount'] = 1

                    questions_dict['answers'] = []
                    questions_dict['answers'].append(answer)

                user = cb.get(str(g.user.id)).value
                user['rep'] += 4
                cb.replace(str(g.user.id), user)
                qb.replace(str(questions_dict['qid']), questions_dict)

                return redirect(url_for('questions', qid=questions_dict['qid'], url=questions_dict['content']['url']))

            qb.replace(str(questions_dict['qid']), questions_dict)
            return render_template('single_question.html', title='Questions', qpage=True, questions=questions_dict,
                                   form=answerForm, fname=g.user.name, user_id=unicode(g.user.id), gravatar=gravatar32)
        else:
            return render_template('single_question.html', title='Questions', qpage=True, questions=questions_dict)


@kunjika.route('/tags/<tag>')
def tags(tag=None):
    return render_template('tags.html')


@kunjika.route('/users/<uid>')
@kunjika.route('/users/<uid>/<uname>')
def users(uid=None, uname=None):
    user = cb.get(uid).value
    #user = json.loads(user)
    gravatar100 = Gravatar(kunjika,
                           size=100,
                           rating='g',
                           default='identicon',
                           force_default=False,
                           force_lower=False)
    if uid in session:
        logged_in = True
        return render_template('users.html', title=user['fname'], user_id=user['id'], fname=user['fname'],
                               lname=user['lname'], email=user['email'], gravatar=gravatar100, logged_in=logged_in,
                               upage=True)
    return render_template('users.html', title=user['fname'], user_id=user['id'], fname=user['fname'],
                           lname=user['lname'], email=user['email'], gravatar=gravatar100, upage=True)


@kunjika.route('/badges/<bid>')
def badge(bid=None):
    return render_template('badge.html')


@kunjika.route('/unanswered/<uid>')
def unanswered(uid=None):
    return render_template('unanswered.html')


@kunjika.route('/ask', methods=['GET', 'POST'])
def ask():
    questionForm = QuestionForm(request.form)
    if g.user is not None and g.user.is_authenticated():
        if questionForm.validate_on_submit() and request.method == 'POST':
            question = {}
            question['content'] = {}
            title = questionForm.question.data
            question['content']['description'] = questionForm.description.data
            question['content']['tags'] = []
            question['content']['tags'] = questionForm.tags.data.split(',')
            question['title'] = title

            url = utility.generate_url(title)

            question['content']['url'] = url
            question['content']['op'] = str(g.user.id)
            question['content']['ts'] = int(time())
            question['content']['ip'] = request.remote_addr
            qb.incr('qcount', 1)
            question['qid'] = qb.get('qcount').value
            question['votes'] = 0
            question['acount'] = 0
            question['views'] = 0

            qb.add(str(question['qid']), question)

            user = cb.get(str(g.user.id)).value
            user['rep'] += 1
            cb.replace(str(g.user.id), user)
            add_tags(question['content']['tags'], question['qid'])

            return redirect(url_for('questions', qid=question['qid'], url=question['content']['url']))

        return render_template('ask.html', title='Ask', form=questionForm, apage=True, fname=g.user.name,
                               user_id=g.user.id)
    return redirect(url_for('login'))


@kunjika.route('/login', methods=['GET', 'POST'])
def login():
    registrationForm = RegistrationForm(request.form)
    loginForm = LoginForm(request.form)

    if loginForm.validate_on_submit() and request.method == 'POST':
        try:
            #document = json.loads(document)
            document = urllib2.urlopen(
                'http://localhost:8092/default/_design/dev_qa/_view/get_id_from_email?key=' + '"' + loginForm.email.data + '"').read()
            document = json.loads(document)['rows'][0]['value']
            print(document)
            if bcrypt.check_password_hash(document['password'], loginForm.password.data):
                session[document['id']] = document['id']
                session['logged_in'] = True
                if 'role' in document:
                    session['admin'] = True
                user = User(document['fname'], document['id'])
                try:
                    login_user(user, remember=True)
                    #print "hello"
                    g.user = user
                    return redirect(url_for('questions'))
                except:
                    return make_response("cant login")

            else:
                render_template('login.html', form=registrationForm, loginForm=loginForm, title='Sign In',
                                providers=kunjika.config['OPENID_PROVIDERS'], lpage=True)

        except:
            return render_template('login.html', form=registrationForm, loginForm=loginForm, title='Sign In',
                                   providers=kunjika.config['OPENID_PROVIDERS'], lpage=True)


    else:
        render_template('login.html', form=registrationForm, loginForm=loginForm, title='Sign In',
                        providers=kunjika.config['OPENID_PROVIDERS'], lpage=True)

    return render_template('login.html', form=registrationForm, loginForm=loginForm, title='Sign In',
                           providers=kunjika.config['OPENID_PROVIDERS'], lpage=True)


@kunjika.route('/register', methods=['POST'])
def register():
    loginForm = LoginForm(request.form)
    registrationForm = RegistrationForm(request.form)

    if registrationForm.validate_on_submit() and request.method == 'POST':
        passwd_hash = bcrypt.generate_password_hash(registrationForm.password.data)

        data = {}

        view = cb._view("dev_qa", "get_role")
        if len(view.value['rows']) == 0:
            data['email'] = registrationForm.email1.data
            data['password'] = passwd_hash
            data['role'] = 'admin'
            data['fname'] = registrationForm.fname.data
            data['lname'] = registrationForm.lname.data
            data['rep'] = 0

            cb.incr('count', 1)
            did = cb.get('count').value
            data['id'] = did
            cb.add(str(did), data)
            user = User(data['fname'], data['id'])
            login_user(user, remember=True)
            g.user = user
            return redirect(url_for('questions'))

        try:
            document = None
            document = cb.get(registrationForm.email1.data).value
        except:
            if document == None:
                data['email'] = registrationForm.email1.data
                data['password'] = passwd_hash
                data['fname'] = registrationForm.fname.data
                data['lname'] = registrationForm.lname.data
                data['rep'] = 0

                cb.incr('count', 1)
                did = cb.get('count').value
                data['id'] = did
                cb.add(str(did), data)

                user = User(data['fname'], did)
                try:
                    login_user(user, remember=True)
                    g.user = user
                    return redirect(url_for('questions'))
                except:
                    return make_response("cant login")

        return render_template('register.html', form=registrationForm, loginForm=loginForm,
                               title='Register', providers=kunjika.config['OPENID_PROVIDERS'], lpage=True)

    return render_template('register.html', form=registrationForm, loginForm=loginForm,
                           title='Register', providers=kunjika.config['OPENID_PROVIDERS'], lpage=True)


@kunjika.route('/check_email', methods=['POST'])
def check_email():
    email = request.form['email']

    try:
        document = cb.get(email)
    except:
        return '1'

    if document != None:
        return '0'


@kunjika.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('questions'))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@kunjika.route('/image_upload', methods=['GET', 'POST'])
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
                data['imagePath'] = "http://localhost:5000/uploads/" + filename
            else:
                data['success'] = "false"
                data['mesage'] = "Invalid image file"

            return json.dumps(data)


@kunjika.route('/get_tags', methods=['GET'])
def get_tags(q=None):
    return json.dumps([{}])


def add_tags(tags_passed, qid):
    for tag in tags_passed:
        try:
            document = tb.get(tag).value
            document['count'] += 1
            document['qid'].append(qid)

            tb.replace(tag, document)

        except:
            data = {}
            data['qid'] = []
            data['tag'] = tag
            data['count'] = 1
            data['qid'].append(qid)

            tb.add(tag, data)


@kunjika.route('/vote_clicked', methods=['GET', 'POST'])
def vote_clicked():
    return votes.handle_vote(request)


@kunjika.route('/edit/<element>', methods=['GET', 'POST'])
def edits(element):
    #edit_list = edit.handle_edit(element)
    #pprint(edit_list)

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
        if type == 'ce':
            if form.validate_on_submit():
                if aid != 0:
                    question['answers'][int(aid) - 1]['comments'][int(cid) - 1]['comment'] = form.comment.data
                else:
                    print "test"
                    question['comments'][int(cid) - 1]['comment'] = form.comment.data

                editor = cb.get(str(g.user.id)).value
                editor['rep'] += 1
                qb.replace(qid, question)

            return redirect(url_for('questions', qid=int(qid), url=utility.generate_url(question['title'])))
        elif type == 'ae':
            if form.validate_on_submit():
                question['answers'][int(aid) - 1]['answer'] = form.answer.data

                editor = cb.get(str(g.user.id)).value
                editor['rep'] += 1
                qb.replace(qid, question)

            return redirect(url_for('questions', qid=int(qid), url=utility.generate_url(question['title'])))
        else:
            if form.validate_on_submit():
                question['content']['description'] = form.description.data

                editor = cb.get(str(g.user.id)).value
                editor['rep'] += 1
                qb.replace(qid, question)
            return redirect(url_for('questions', qid=int(qid), url=utility.generate_url(question['title'])))
    else:
        return render_template('edit.html', title='Edit', form=form, question=question, type=type, qid=qid,
                               aid=int(aid), cid=int(cid))


@kunjika.route('/answer_accepted')
def answer_accepted():
    return utility.accept_answer(request.args.get('id'))


@kunjika.route('/favorited')
def favorited():
    return utility.handle_favorite(request.args.get('id'))

@kunjika.route('/postcomment', methods=['GET', 'POST'])
def postcomment():
    #print request.form
    #print type(request.form['comment'])
    if len(request.form['comment']) < 10 or len(request.form['comment']) > 5000:
        return "Comment must be between 10 and 5000 characters."
    else:
        elements = request.form['element'].split('-')
        qid = elements[0]
        #print "qid = " + qid
        aid = 0
        if len(elements) == 2: # check if comment has been made on answers
            aid = elements[1]
            #print "aid = ",  aid   # if it is on question aid will be zero

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

    pprint(question)

    qb.replace(str(qid), question)
    ts = strftime("%a, %d %b %Y %H:%M", localtime(comment['ts']))
    #return '<div class="comment" id="c-' + str(comment['cid']) + '">' + request.form['comment'] +'<div>&mdash;</div>' \
    #       '<a href="/users/"' + str(g.user.id) + '/' + g.user.name + '>' + g.user.name +'</a> ' + str(ts) +'</div>'
    return json.dumps({"id": comment['cid'], "comment": request.form['comment'], "user_id": g.user.id,
                       "uname": g.user.name, "ts": ts})


@kunjika.route('/unanswered')
def unanswered():
    questions_list = question.get_questions()
    if g.user is None:
        return render_template('unanswered.html', title='Unanswered questions', unpage=True, questions=questions_list)
    elif g.user is not None and g.user.is_authenticated():
        return render_template('unanswered.html', title='Unanswered questions', unpage=True, questions=questions_list,
        fname=g.user.name, user_id=g.user.id)
    else:
        return render_template('unanswered.html', title='Unanswered questions', unpage=True, questions=questions_list)

if __name__ == '__main__':
    kunjika.run()

