from flask import Flask, session, render_template, abort, redirect, url_for, flash, make_response, request
import json
from forms import *
from flaskext.bcrypt import Bcrypt
from couchbase.couchbaseclient import VBucketAwareCouchbaseClient as CbClient
from couchbase.client import Couchbase
import urllib2
from pprint import pprint
from flaskext.gravatar import Gravatar
from werkzeug import secure_filename, SharedDataMiddleware
import os
from os.path import basename
import time

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
    '/uploads': kunjika.config['UPLOAD_FOLDER']
})

cb = CbClient("http://localhost:8091/pools/default", "default", "")
#bucket = cb["bucket"]

cb1 = Couchbase("localhost", "shiv", "yagyavalkya")
bucket = cb1["default"]

qc = CbClient("http://localhost:8091/pools/default", "questions", "")

qbucket = Couchbase("localhost", "shiv", "yagyavalkya")
qb = qbucket["questions"]

#Initialize count at first run. Later it is useless
try:
    cb.add('count', 0, 0, json.dumps(0))
except:
    pass

bcrypt = Bcrypt(kunjika)


@kunjika.route('/', methods=['GET', 'POST'])
@kunjika.route('/questions', methods=['GET', 'POST'])
@kunjika.route('/questions/<qid>')
def questions(qid=None, uid=None, name=None, email=None):
    uid = request.args.get('uid', '')
    name = request.args.get('name', '')
    qid = request.args.get('qid', '')
    try:
        if isinstance(uid, (unicode)):
            resp = make_response(render_template('questions.html', title='Questions',
                                                 user_name=name, user_id=uid, logged_in=True))
            resp.headers['Cache-Control'] = 'no-cache'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = 0
            resp.set_cookie('uid', uid)
            return resp
    except:
        pass

    return render_template('questions.html', title='Questions')


@kunjika.route('/tags/<tag>')
def tags(tag=None):
    return render_template('tags.html')


@kunjika.route('/users/<uid>')
def users(uid=None):
    user = cb.get(uid)[2]
    user = json.loads(user)
    gravatar = Gravatar(kunjika,
                        size=100,
                        rating='g',
                        default='identicon',
                        force_default=False,
                        force_lower=False)
    if uid in session:
        logged_in = True
        return render_template('users.html', title=user['fname'], user_id=user['id'], fname=user['fname'],
                               lname=user['lname'], email=user['email'], gravatar=gravatar, logged_in=logged_in)
    return render_template('users.html', title=user['fname'], user_id=user['id'], fname=user['fname'],
                           lname=user['lname'], email=user['email'], gravatar=gravatar)

    #return render_template('users.html')


@kunjika.route('/badges/<bid>')
def badge(bid=None):
    return render_template('badge.html')


@kunjika.route('/unanswered/<uid>')
def unanswered(uid=None):
    return render_template('unanswered.html')


@kunjika.route('/ask', methods=['GET', 'POST'])
def ask(uid=None):
    questionForm = QuestionForm(request.form)

    if questionForm.validate_on_submit() and request.method == 'POST':
        title = questionForm.question.data
        print questionForm.description.data
        print questionForm.tags.data
        length = len(title)
        print length
        prev_dash = False
        title = title.lower()
        new_title = ""
        for i in range(length):
            c = title[i]
            if c == ' ' or c == ',' or c == '.' or c == '/' or c == '\\' or c == '-':
                if not prev_dash:
                    new_title += '-'
                    prev_dash = True
            elif ord(c) > 160:
                c = c.decode('UTF-8').lower()
                new_title += c
                prev_dash = False
            else:
                new_title += c
                prev_dash = False
        print new_title
    elif request is not None:
        uid = request.cookies.get('uid')
        user = cb.get(uid)[2]
        user = json.loads(user)
        if uid in session:
            return render_template('ask.html', title='ask', form=questionForm, user_id=user['id'], fname=user['fname'],
                                   lname=user['lname'], email=user['email'], logged_in=True)

    return redirect(url_for('login'))


@kunjika.route('/login', methods=['GET', 'POST'])
def login():
    registrationForm = RegistrationForm(request.form)
    loginForm = LoginForm(request.form)

    if loginForm.validate_on_submit() and request.method == 'POST':
        try:
            #document = json.loads(document)
            document = urllib2.urlopen(
                "http://localhost:8092/default/_design/dev_get_role/_view/get_id_from_email?key=" + '"' + loginForm.email.data + '"').read()
            document = json.loads(document)
            did = document['rows'][0]['id']
            document = cb.get(did)[2]
            document = json.loads(document)
            #print document['email'] + " " + document['password']
            #print loginForm.email.data + " " + loginForm.password.data
            #print document['id']
            if bcrypt.check_password_hash(document['password'], loginForm.password.data):
                session[did] = did
                #print document['email']
                session['logged_in'] = True
                if 'role' in document:
                    session['admin'] = True

                return redirect(url_for('questions', qid=0, uid=did, name=document['fname']))
            #return redirect(url_for('/'))

            else:
                #print "Hello"
                render_template('login.html', form=registrationForm, loginForm=loginForm, title='Sign In',
                                providers=kunjika.config['OPENID_PROVIDERS'])

        except:
            return redirect(url_for('questions'))
            #render_template('login.html', form = registrationForm, loginForm=loginForm, title='Sign In',
            #                providers = kunjika.config['OPENID_PROVIDERS'])

    else:
        render_template('login.html', form=registrationForm, loginForm=loginForm, title='Sign In',
                        providers=kunjika.config['OPENID_PROVIDERS'])

    return render_template('login.html', form=registrationForm, loginForm=loginForm, title='Sign In',
                           providers=kunjika.config['OPENID_PROVIDERS'])


@kunjika.route('/register', methods=['POST'])
def register():
    loginForm = LoginForm(request.form)
    registrationForm = RegistrationForm(request.form)

    if registrationForm.validate_on_submit() and request.method == 'POST':
        passwd_hash = bcrypt.generate_password_hash(registrationForm.password.data)

        #document = None
        data = {}

        view = bucket.view("_design/dev_get_role/_view/get_role")

        if len(view) == 0:
            data['email'] = registrationForm.email1.data
            data['password'] = passwd_hash
            data['role'] = 'admin'
            data['fname'] = registrationForm.fname.data
            data['lname'] = registrationForm.lname.data

            cb.incr('count', 1)
            did = cb.get('count')[2]
            data['id'] = did
            cb.add(str(did), 0, 0, json.dumps(data))

            return redirect(url_for('questions'))

        try:
            document = None
            document = cb.get(registrationForm.email1.data)
        except:
            if document == None:
                data['email'] = registrationForm.email1.data
                data['password'] = passwd_hash
                data['fname'] = registrationForm.fname.data
                data['lname'] = registrationForm.lname.data

                cb.incr('count', 1)
                did = cb.get('count')[2]
                data['id'] = did
                cb.add(str(did), 0, 0, json.dumps(data))

                return redirect(url_for('questions'))

        return render_template('register.html', form=registrationForm, loginForm=loginForm,
                               title='Register', providers=kunjika.config['OPENID_PROVIDERS'])

    return render_template('register.html', form=registrationForm, loginForm=loginForm,
                           title='Register', providers=kunjika.config['OPENID_PROVIDERS'])


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
    uid = request.cookies.get('uid')
    if uid == 1:
        session['admin'] = False
    if uid:
        session.pop(uid, None)
    if 'admin' in session:
        session.pop('admin', None)

    for k, v in session.iteritems():
        print str(k) + " " + str(v)

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
            print extension
            print filename
            f = filename
            new_filename = ""
            while saved != True:
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

            if saved == True:
                data['success'] = "true"
                data['imagePath'] = "http://localhost:5000/uploads/" + filename
            else:
                data['success'] = "false"
                data['mesage'] = "Invalid image file"

            return json.dumps(data)


@kunjika.route('/get_tags', methods=['GET'])
def get_tags(q=None):
    return json.dumps([{"id": "0", "name": "0"}])


if __name__ == '__main__':
    kunjika.run()
