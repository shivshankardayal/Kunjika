from flask import Flask
from flask import render_template
from flask import abort, redirect, url_for, flash
from flask import request
import json
from register import RegistrationForm, LoginForm
from pymongo import *
from flaskext.bcrypt import Bcrypt
from couchbase.couchbaseclient import VBucketAwareCouchbaseClient as CbClient

kunjika = Flask(__name__)

kunjika.config.from_object('config')
kunjika.debug = True

cb = CbClient("http://localhost:8091/pools/default","default", "")

bcrypt = Bcrypt(kunjika)

@kunjika.route('/')
@kunjika.route('/questions', methods=['GET', 'POST'])
#@kunjika.route('/questions/<qid>')
def questions(qid=None):
    return render_template('questions.html', title='Questions')

@kunjika.route('/tags/<tag>')
def tags(tag=None):
    return render_template('tags.html')

@kunjika.route('/users/<uid>')
def users(uid=None):
    return render_template('users.html')

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
            document = cb.get(loginForm.email.data)[2]
            document = json.loads(document)
            print document['password']
            print bcrypt.generate_password_hash(loginForm.password.data)
            if (document['email'] == loginForm.email.data) and bcrypt.check_password_hash(document['password'], loginForm.password.data):
                return redirect(url_for('questions'))
            else:
                render_template('login.html', form = registrationForm, loginForm=loginForm, title='Sign In',
                                providers = kunjika.config['OPENID_PROVIDERS'])

        except:
            render_template('login.html', form = registrationForm, loginForm=loginForm, title='Sign In',
                            providers = kunjika.config['OPENID_PROVIDERS'])
            
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

        role = None
        data = {}

        try:
            role = cb.get('role')
        except:
            if role == 'admin':
                data['email'] = registrationForm.email1.data
                data['password'] = passwd_hash
                data['role'] = 'admin'
                data['fname'] = registrationForm.fname.data
                data['lname'] = registrationForm.lname.data

                cb.add(data['email'], 0, 0, json.dumps(data))

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

                cb.add(data['email'], 0, 0, json.dumps(data)) 
                return redirect(url_for('questions'))

        return render_template('register.html', form = registrationForm, loginForm=loginForm,
                                   title='Sign In', providers = kunjika.config['OPENID_PROVIDERS'])


@kunjika.route('/check_email', methods=['POST'])
def check_email():

    email = request.form['email']

    try:
        document = cb.get(email)
    except:
        return '1'

    if document != None:
        return '0'

if __name__ == '__main__':
    kunjika.run()
