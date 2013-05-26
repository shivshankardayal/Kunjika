from flask import Flask, session
from flask import render_template
from flask import abort, redirect, url_for, flash, make_response
from flask import request
import json
from register import RegistrationForm, LoginForm
from pymongo import *
from flaskext.bcrypt import Bcrypt
from couchbase.couchbaseclient import VBucketAwareCouchbaseClient as CbClient
from couchbase.client import Couchbase
import uuid
import urllib2
from pprint import pprint
from flaskext.gravatar import Gravatar

kunjika = Flask(__name__)

kunjika.config.from_object('config')
kunjika.debug = True

cb = CbClient("http://localhost:8091/pools/default","default", "")
#bucket = cb["bucket"]

cb1 = Couchbase("localhost", "shiv", "yagyavalkya")
bucket = cb1["default"]

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
def users(uid=None, name=None):
    user = cb.get(uid)[2]
    user = json.loads(user)
    gravatar = Gravatar(kunjika,
                    size=100,
                    rating='g',
                    default='identicon',
                    force_default=False,
                    force_lower=False)
    if session[uid]:
        logged_in=True
    return render_template('users.html', title=user['fname'], user_id=user['id'], fname=user['fname'], lname=user['lname'], email=user['email'], gravatar=gravatar, logged_in=logged_in)
    #return render_template('users.html')

@kunjika.route('/badges/<bid>')
def badge(bid=None):
    return render_template('badge.html')

@kunjika.route('/unanswered/<uid>')
def unanswered(uid=None):
    return render_template('unanswered.html')

@kunjika.route('/ask')
def ask():
    return render_template('ask.html')

@kunjika.route('/login', methods=['GET', 'POST'])
def login():
    registrationForm = RegistrationForm(request.form)
    loginForm = LoginForm(request.form)

    if loginForm.validate_on_submit() and request.method == 'POST':
        try:
            #document = json.loads(document)
            document = urllib2.urlopen("http://localhost:8092/default/_design/dev_get_role/_view/get_id_from_email?key=" + '"' + loginForm.email.data +'"').read()
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
                render_template('login.html', form = registrationForm, loginForm=loginForm, title='Sign In',
                                providers = kunjika.config['OPENID_PROVIDERS'])

        except:
            return redirect(url_for('questions'))
            #render_template('login.html', form = registrationForm, loginForm=loginForm, title='Sign In',
            #                providers = kunjika.config['OPENID_PROVIDERS'])
            
    else:
        render_template('login.html', form = registrationForm, loginForm=loginForm, title='Sign In',
                        providers = kunjika.config['OPENID_PROVIDERS'])

    return render_template('login.html', form = registrationForm, loginForm=loginForm, title='Sign In',
                           providers = kunjika.config['OPENID_PROVIDERS'])

@kunjika.route('/register', methods=['POST'])
def register():
    loginForm = LoginForm(request.form)
    registrationForm = RegistrationForm(request.form)

    if registrationForm.validate_on_submit() and request.method =='POST':
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

        return render_template('register.html', form = registrationForm, loginForm=loginForm,
                               title='Register', providers = kunjika.config['OPENID_PROVIDERS'])

    return render_template('register.html', form = registrationForm, loginForm=loginForm,
                           title='Register', providers = kunjika.config['OPENID_PROVIDERS'])

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

if __name__ == '__main__':
    kunjika.run()
