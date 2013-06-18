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
import datetime
from flask.ext.login import (LoginManager, current_user, login_required,
                             login_user, logout_user, UserMixin, AnonymousUser,
                             confirm_login, fresh_login_required)
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
from config import OPENID_PROVIDERS

UPLOAD_FOLDER = '/home/shiv/Kunjika/uploads'
ALLOWED_EXTENSIONS = set(['gif','png','jpg','jpeg', 'txt', 'c', 'cc', 'cpp', 'C', 'java', 'php', 'py', 'rb',
                          'zip', 'gz', 'bz2', '7z', 'pdf', 'epub', 'css', 'js', 'html', 'h', 'hh', 'hpp', 'svg'])

kunjika = Flask(__name__)
kunjika.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
kunjika.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
kunjika.config.from_object('config')
kunjika.debug = True
kunjika.add_url_rule('/uploads/<filename>', 'uploaded_file',
                     build_only=True)
kunjika.wsgi_app = SharedDataMiddleware(kunjika.wsgi_app, {
    '/uploads': kunjika.config['UPLOAD_FOLDER']})
QUESTIONS_PER_PAGE = kunjika.config['QUESTIONS_PER_PAGE']
TAGS_PER_PAGE = kunjika.config['TAGS_PER_PAGE']
USERS_PER_PAGE = kunjika.config['USERS_PER_PAGE']

oid = OpenID(kunjika, '/tmp')

mail = Mail(kunjika)
admin = kunjika.config['ADMIN_EMAIL']

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

#Initialize question count at first run. Later it is useless
try:
    tb.add('tcount', 0)
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

kunjika.jinja_env.globals['url_for_other_page'] = utility.url_for_other_page

@kunjika.before_request
def before_request():
    g.user = current_user

def get_user(uid):
    try:
        user_from_db = cb.get(str(uid)).value
        return User(user_from_db['name'], user_from_db['id'])
    except NotFoundError:
        return None


@lm.user_loader
def load_user(uid):
    #print id
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
    tag_list = []
    try:
        qcount = qb.get('qcount').value
        ucount = cb.get('count').value
        tcount = tb.get('tcount').value
        acount = urllib2.urlopen('http://localhost:8092/questions/_design/dev_dev/_view/get_acount').read()
        acount = json.loads(acount)
        if len(acount['rows']) is not 0:
            acount = acount['rows'][0]['value']
        else:
            acount = 0
        if tcount > 0:
            tag_list = utility.get_popular_tags()
    except:
        pass
    questions_dict = {}
    if tag is not None:
        questions_list = utility.get_questions_for_tag(page, QUESTIONS_PER_PAGE, tag)
        count = len(questions_list)
        if not questions_list and page != 1:
            abort(404)
        pagination = utility.Pagination(page, QUESTIONS_PER_PAGE, count)
        if g.user is None:
            return render_template('questions.html', title='Questions', qpage=True, questions=questions_list,
                                   pagination=pagination, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)
        elif g.user is not None and g.user.is_authenticated():
            return render_template('questions.html', title='Questions', qpage=True, questions=questions_list,
                                   name=g.user.name, user_id=g.user.id, pagination=pagination, qcount=qcount,
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
                                   name=g.user.name, user_id=g.user.id, pagination=pagination, qcount=qcount,
                                   ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)
        else:
            return render_template('questions.html', title='Questions', qpage=True, questions=questions_list,
                                   pagination=pagination, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)
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
                                   form=answerForm, name=g.user.name, user_id=unicode(g.user.id), gravatar=gravatar32,
                                   qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)
        else:
            return render_template('single_question.html', title='Questions', qpage=True, questions=questions_dict,
                                   qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)


'''@kunjika.route('/tags/<tag>')
def tags(tag=None):
    qcount = qb.get('qcount').value
    ucount = cb.get('count').value
    tcount = tb.get('tcount').value
    acount = urllib2.urlopen('http://localhost:8092/questions/_design/dev_dev/_view/get_acount').read()
    acount = json.loads(acount)
    if len(acount['rows']) is not 0:
        acount = acount['rows'][0]['value']
    else:
        acount = 0
    return render_template('tags.html')
'''

@kunjika.route('/users/<uid>')
@kunjika.route('/users/<uid>/<uname>')
def users(uid=None, uname=None):
    tag_list = []
    qcount = qb.get('qcount').value
    ucount = cb.get('count').value
    tcount = tb.get('tcount').value
    acount = urllib2.urlopen('http://localhost:8092/questions/_design/dev_dev/_view/get_acount').read()
    acount = json.loads(acount)
    if len(acount['rows']) is not 0:
        acount = acount['rows'][0]['value']
    else:
        acount = 0

    if tcount > 0:
        tag_list = utility.get_popular_tags()
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
        return render_template('users.html', title=user['name'], user_id=user['id'], name=user['name'], fname=user['fname'],
                               lname=user['lname'], email=user['email'], gravatar=gravatar100, logged_in=logged_in,
                               upage=True, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)
    return render_template('users.html', title=user['name'], lname=user['lname'], email=user['email'], gravatar=gravatar100, upage=True,
                           qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)

'''@kunjika.route('/unanswered/<uid>')
def unanswered(uid=None):
    tag_list = utility.get_popular_tags()
    qcount = qb.get('qcount').value
    ucount = cb.get('count').value
    tcount = tb.get('tcount').value
    acount = urllib2.urlopen('http://localhost:8092/questions/_design/dev_dev/_view/get_acount').read()
    acount = json.loads(acount)
    acount = acount['rows'][0]['value']
    return render_template('unanswered.html', qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)
'''

@kunjika.route('/ask', methods=['GET', 'POST'])
def ask():
    tag_list = []
    qcount = qb.get('qcount').value
    ucount = cb.get('count').value
    tcount = tb.get('tcount').value
    acount = urllib2.urlopen('http://localhost:8092/questions/_design/dev_dev/_view/get_acount').read()
    acount = json.loads(acount)
    if len(acount['rows']) is not 0:
        acount = acount['rows'][0]['value']
    else:
        acount = 0

    if tcount > 0:
        tag_list = utility.get_popular_tags()
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
            if not questions in user:
                user['questions'] = []
                user['questions'].append(question['qid'])
            else:
                user['questions'].append(question['qid'])

            cb.replace(str(g.user.id), user)
            add_tags(question['content']['tags'], question['qid'])

            return redirect(url_for('questions', qid=question['qid'], url=question['content']['url']))

        return render_template('ask.html', title='Ask', form=questionForm, apage=True, name=g.user.name,
                               user_id=g.user.id, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)
    return redirect(url_for('login'))

@kunjika.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    if request.args.get('email') is None:
        return redirect('/')
    document = None
    profileForm = ProfileForm(request.form)
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('/'))
    if profileForm.validate_on_submit() and request.method == 'POST':
        data = {}
        print profileForm.email2.data
        view = urllib2.urlopen('http://localhost:8092/default/_design/dev_qa/_view/get_role?stale=false').read()
        view = json.loads(view)
        if len(view['rows']) == 0:
            print "hello1"
            data['email'] = profileForm.email2.data
            data['role'] = 'admin'
            data['fname'] = profileForm.fname.data
            data['lname'] = profileForm.lname.data
            data['name'] = data['fname'] + " " + data['lname']
            data['rep'] = 0

            cb.incr('count', 1)
            did = cb.get('count').value
            data['id'] = did
            cb.add(str(did), data)
            user = User(data['name'], data['id'])
            login_user(user, remember=True)
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
            'http://localhost:8092/default/_design/dev_qa/_view/get_id_from_email?key=' + '"' + profileForm.email2.data + '"&stale=false').read()
        document = json.loads(document)
        #print(document)
        if len(document['rows']) == 0:
            print "hello2"
            data['email'] = profileForm.email2.data
            data['fname'] = profileForm.fname.data
            data['lname'] = profileForm.lname.data
            data['name'] = data['fname'] + " " + data['lname']
            data['rep'] = 0

            cb.incr('count', 1)
            did = cb.get('count').value
            data['id'] = did
            cb.add(str(did), data)
            user = User(data['name'], did)
            login_user(user, remember=True)
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
    return render_template('create_profile.html', form=profileForm,
                           title="Create Profile", lpage=True, next=oid.get_next_url())

@oid.after_login
def create_or_login(resp):
    session['openid'] = resp.identity_url
    user = utility.filter_by(resp.email)
    if user is not None:
        flash(u'Successfully signed in')

        g.user = user
        print user
        session[user['id']] = user['id']
        session['logged_in'] = True
        if 'role' in user:
            user['admin'] = True
        user = User(user['name'], user['id'])
        try:
            login_user(user, remember=True)
            g.user = user
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
    openidForm = OpenIDForm(request.form)

    print g.user

    if g.user is not AnonymousUser and g.user.is_authenticated():
        return redirect(oid.get_next_url())
    if openidForm.validate_on_submit() and request.method == 'POST':
        openid = request.form.get('openid')
        googleid = request.form.get('googleid')
        yahooid = request.form.get('yahooid')
        #print openid
        #print yahooid
        #print googleid
        if googleid:
            return oid.try_login('https://www.google.com/accounts/o8/id', ask_for=['email', 'fullname', 'nickname'])
        elif yahooid:
            return oid.try_login('https://me.yahoo.com', ask_for=['email', 'fullname', 'nickname'])
        elif openid:
            return oid.try_login(openid, ask_for=['email', 'fullname', 'nickname'])
    return render_template('openid.html', form=registrationForm, loginForm=loginForm, openidForm=openidForm, title='Sign In',
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
                'http://localhost:8092/default/_design/dev_qa/_view/get_id_from_email?key=' + '"' + loginForm.email.data + '"').read()
            document = json.loads(document)['rows'][0]['value']
            #print(document)
            if bcrypt.check_password_hash(document['password'], loginForm.password.data):
                session[document['id']] = document['id']
                session['logged_in'] = True
                if 'role' in document:
                    session['admin'] = True
                user = User(document['name'], document['id'])
                try:
                    login_user(user, remember=True)
                    #print "hello"
                    g.user = user
                    return redirect(url_for('questions'))
                except:
                    return make_response("cant login")

            else:
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
        view = urllib2.urlopen('http://localhost:8092/default/_design/dev_qa/_view/get_role?stale=false').read()
        view = json.loads(view)
        if len(view['rows']) == 0:
            data['email'] = registrationForm.email1.data
            data['password'] = passwd_hash
            data['role'] = 'admin'
            data['fname'] = registrationForm.fname.data
            data['lname'] = registrationForm.lname.data
            data['name'] = data['fname'] + " " + data['lname']
            data['rep'] = 0

            cb.incr('count', 1)
            did = cb.get('count').value
            data['id'] = did
            cb.add(str(did), data)
            user = User(data['name'], data['id'])
            login_user(user, remember=True)
            g.user = user

            return redirect(url_for('questions'))

        document = urllib2.urlopen(
            'http://localhost:8092/default/_design/dev_qa/_view/get_id_from_email?key=' + '"' + registrationForm.email1.data + '"&stale=false').read()
        document = json.loads(document)
        #print(document)
        if len(document['rows']) == 0:
            data['email'] = registrationForm.email1.data
            data['password'] = passwd_hash
            data['fname'] = registrationForm.fname.data
            data['lname'] = registrationForm.lname.data
            data['name'] = data['fname'] + " " + data['lname']
            data['rep'] = 0

            cb.incr('count', 1)
            did = cb.get('count').value
            data['id'] = did
            cb.add(str(did), data)

            user = User(data['name'], did)
            try:
                login_user(user, remember=True)
                g.user = user
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


@kunjika.route('/get_tags/<qid>', methods=['GET', 'POST'])
def get_tags(q=None, qid=None):
    #print request.args.get('q')

    if qid is not None:
        question = qb.get(str(qid)).value

        tags = question['content']['tags']

        tags_list = []
        for i in tags:
            tag = urllib2.urlopen('http://localhost:8092/tags/_design/dev_qa/_view/get_doc_from_tag?key=' + '"' + str(i) + '"').read()
            #print tag
            tag = json.loads(tag)['rows'][0]['value']
            tags_list.append({"id": tag['tid'], "name": tag['tag']})
    #print tags_list
    return json.dumps(tags_list)


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
            data['excerpt'] = ""
            data['tag'] = tag
            data['count'] = 1
            data['qid'].append(qid)
            tb.incr('tcount', 1)
            tid = tb.get('tcount').value
            data['tid'] = tid

            tb.add(tag, data)

def replace_tags(tags_passed, qid, current_tags):
    for tag in tags_passed:
        if tag not in current_tags:
            try:
                document = tb.get(tag).value
                document['count'] += 1
                document['qid'].append(qid)
                tb.replace(tag, document)

            except:
                data = {}
                data['qid'] = []
                data['excerpt'] = ""
                data['tag'] = tag
                data['count'] = 1
                data['qid'].append(qid)
                tb.incr('tcount', 1)
                tid = tb.get('tcount').value
                data['tid'] = tid

                tb.add(tag, data)

    for tag in current_tags:
        if tag not in tags_passed:
            tag = urllib2.urlopen('http://localhost:8092/tags/_design/dev_qa/_view/get_doc_from_tag?key=' + '"' + str(tag) + '"').read()
            #print tag
            tag = json.loads(tag)['rows'][0]['value']
            tag['qid'].remove(int(qid))
            tag['count'] -= 1

            tb.replace(tag['tag'], tag)

@kunjika.route('/vote_clicked', methods=['GET', 'POST'])
def vote_clicked():
    return votes.handle_vote(request)


@kunjika.route('/edit/<element>', methods=['GET', 'POST'])
def edits(element):
    tag_list = []
    qcount = qb.get('qcount').value
    ucount = cb.get('count').value
    tcount = tb.get('tcount').value
    acount = urllib2.urlopen('http://localhost:8092/questions/_design/dev_dev/_view/get_acount').read()
    acount = json.loads(acount)
    if len(acount['rows']) is not 0:
        acount = acount['rows'][0]['value']
    else:
        acount = 0
    if tcount > 0:
        tag_list = utility.get_popular_tags()
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
                tags = form.tags.data.split(',')
                tag_list = []
                current_tags = question['content']['tags']
                for tag in tags:
                    try:
                        tag = int(tag)
                        tag = urllib2.urlopen('http://localhost:8092/tags/_design/dev_qa/_view/get_tag_by_id?key=' + str(tag)).read()
                        tag = json.loads(tag)['rows'][0]['value']
                        tag_list.append(tag['tag'])
                    except:
                        tag_list.append(tag)

                question['content']['tags'] = tag_list
                editor = cb.get(str(g.user.id)).value
                editor['rep'] += 1
                qb.replace(str(qid), question)
                replace_tags(question['content']['tags'], question['qid'], current_tags)
            return redirect(url_for('questions', qid=int(qid), url=utility.generate_url(question['title'])))
    else:
        return render_template('edit.html', title='Edit', form=form, question=question, type=type, qid=qid,
                               aid=int(aid), cid=int(cid), qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)


@kunjika.route('/answer_accepted')
def answer_accepted():
    return utility.accept_answer(request.args.get('id'))


@kunjika.route('/favorited')
def favorited():
    return utility.handle_favorite(request.args.get('id'))

@kunjika.route('/flag')
def flag():
    return utility.flag(request.args.get('id'))

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

    #pprint(question)

    qb.replace(str(qid), question)
    ts = strftime("%a, %d %b %Y %H:%M", localtime(comment['ts']))
    #return '<div class="comment" id="c-' + str(comment['cid']) + '">' + request.form['comment'] +'<div>&mdash;</div>' \
    #       '<a href="/users/"' + str(g.user.id) + '/' + g.user.name + '>' + g.user.name +'</a> ' + str(ts) +'</div>'
    return json.dumps({"id": comment['cid'], "comment": request.form['comment'], "user_id": g.user.id,
                       "uname": g.user.name, "ts": ts})


@kunjika.route('/unanswered', defaults={'page': 1})
@kunjika.route('/unanswered/page/<int:page>')
def unanswered(page):
    tag_list = []
    qcount = qb.get('qcount').value
    ucount = cb.get('count').value
    tcount = tb.get('tcount').value
    acount = urllib2.urlopen('http://localhost:8092/questions/_design/dev_dev/_view/get_acount').read()
    acount = json.loads(acount)
    if len(acount['rows']) is not 0:
        acount = acount['rows'][0]['value']
    else:
        acount = 0
    if tcount > 0:
        tag_list = utility.get_popular_tags()
    skip = (page - 1) * QUESTIONS_PER_PAGE
    questions = urllib2.urlopen(
        'http://localhost:8092/questions/_design/dev_dev/_view/get_unanswered?limit=' +
        str(QUESTIONS_PER_PAGE) + '&skip=' + str(skip) + '&descending=true').read()
    questions = json.loads(questions)
    count = questions['total_rows']
    #print questions
    questions_list = []
    for i in questions['rows']:
        questions_list.append(i['value'])

    for i in questions_list:
        i['tstamp'] = strftime("%a, %d %b %Y %H:%M", localtime(i['content']['ts']))

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
                               name=g.user.name, user_id=g.user.id, pagination=pagination,
                               qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)
    else:
        return render_template('unanswered.html', title='Unanswered questions', unpage=True, questions=questions_list,
                               pagination=pagination, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)


@kunjika.route('/users/', defaults={'page': 1})
@kunjika.route('/users/page/<int:page>')
def show_users(page):
    tag_list = []
    qcount = qb.get('qcount').value
    ucount = cb.get('count').value
    tcount = tb.get('tcount').value
    acount = urllib2.urlopen('http://localhost:8092/questions/_design/dev_dev/_view/get_acount').read()
    acount = json.loads(acount)
    if len(acount['rows']) is not 0:
        acount = acount['rows'][0]['value']
    else:
        acount = 0
    if tcount > 0:
        tag_list = utility.get_popular_tags()
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
                               name=g.user.name, user_id=g.user.id)
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
    acount = urllib2.urlopen('http://localhost:8092/questions/_design/dev_dev/_view/get_acount').read()
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
                               name=g.user.name, user_id=g.user.id, acount=acount, tag_list=tag_list)
    return render_template('tags.html', title='Tags', tpage=True, pagination=pagination, tags=tags,
                           no_of_tags=no_of_tags, qcount=qcount, ucount=ucount, tcount=tcount, acount=acount, tag_list=tag_list)

def make_external(url):
    return urljoin(request.url_root, url)

@kunjika.route('/recent_questions.atom')
def recent_feed():
    feed = AtomFeed('Recent Questions',
                    feed_url=request.url, url=request.url_root)
    questions = urllib2.urlopen('http://localhost:8092/questions/_design/dev_dev/_view/get_questions?limit=' + str(50)).read()
    questions = json.loads(questions)['rows']

    question_list = []
    for i in questions:
        question_list.append(i['value'])


    for question in question_list:
        feed.add(question['title'], unicode(question['content']['description']),
                 content_type='html',
                 author='http://localhost:5000/users/' + unicode(question['content']['op']) + question['opname'],
                 url=make_external('http://localhost:5000/questions' + '/' + unicode(question['qid']) + "/" + question['content']['url']),
                 updated=datetime.datetime(2013, 05, 17))
    return feed.get_response()

if __name__ == '__main__':
    kunjika.run()

