from flask import Flask
from flask import render_template
from flask import abort, redirect, url_for, flash
from flask import request
from register import RegistrationForm, LoginForm
from flask_pymongo import PyMongo
from pymongo import *
from flaskext.bcrypt import Bcrypt

kunjika = Flask(__name__)

kunjika.config.from_object('config')
kunjika.debug = True

mongo = PyMongo(kunjika)
connection = Connection(kunjika.config['DB_HOST'], kunjika.config['DB_PORT'])
db = connection.kunjika

bcrypt = Bcrypt(kunjika)

@kunjika.route('/')
@kunjika.route('/questions')
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
        return redirect(url_for('questions'))
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
        document = db.users.find({"uid":0})
        if document.count() == 0:
            #global max_id
            #max_id += 1
            db.users.insert({'email': registrationForm.email1.data, 'password': passwd_hash, 'role': 'admin',
                            'fname': registrationForm.fname.data, 'lname' :registrationForm.lname.data})
            return redirect(url_for('questions'))

        document = db.users.find({'email': registrationForm.email1.data})

        if document.count() == 0:
            db.users.insert({'email': registrationForm.email1.data, 'password': passwd_hash,
                            'fname': registrationForm.fname.data, 'lname' :registrationForm.lname.data, 'role': 'user'})
        else:
            return render_template('register.html', form = registrationForm, loginForm=loginForm,
                                   title='Sign In', providers = kunjika.config['OPENID_PROVIDERS'])

        return redirect(url_for('questions'))
    else:
            return render_template('register.html', form = registrationForm, loginForm=loginForm,
                                   title='Sign In', providers = kunjika.config['OPENID_PROVIDERS'])

@kunjika.route('/check_email', methods=['POST'])
def check_email():

    email = request.form['email']

    document = db.users.find({"email": email})

    if document.count() == 1:
        return '0'
    else:
        return '1'

if __name__ == '__main__':
    kunjika.run()
