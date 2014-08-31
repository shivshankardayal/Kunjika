from flask import Flask, redirect, url_for, session, request, jsonify, Blueprint, flash
from flask_oauthlib.client import OAuth, OAuthException
import json
import kunjika

OA = Blueprint('oauth', __name__, template_folder='templates')

oauth = OAuth(kunjika)

google = oauth.remote_app(
    'google',
    consumer_key=kunjika.GOOGLE_ID,
    consumer_secret=kunjika.GOOGLE_SECRET,
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/userinfo.email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

facebook = oauth.remote_app(
    'facebook',
    consumer_key=kunjika.FACEBOOK_ID,
    consumer_secret=kunjika.FACEBOOK_SECRET,
    request_token_params={'scope': 'email'},
    base_url='https://graph.facebook.com',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth'
)


# Twitter does not supply email so cannot be used.
# Linkedin is postponed for later
'''
twitter = oauth.remote_app(
    'twitter',
    consumer_key=kunjika.TWITTER_KEY,
    consumer_secret=kunjika.TWITTER_SECRET,
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
)

linkedin = oauth.remote_app(
        'linkedin',
    consumer_key=kunjika.LINKEDIN_KEY,
    consumer_secret=kunjika.TWITTER_SECRET,
    request_token_params={
        'scope': 'r_basicprofile',
        'state': 'RandomString',
    },
    base_url='https://api.linkedin.com/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
    authorize_url='https://www.linkedin.com/uas/oauth2/authorization',
)
'''

@OA.route('/google_login')
def g_login():
    return google.authorize(callback=url_for('oauth.g_authorized', _external=True))


@OA.route('/google_login/authorized')
def g_authorized():
    resp = google.authorized_response()
    if resp is None:
        flash('OAuth login is denied!', 'error')
        return redirect(url_for('questions'))

    session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')
    if 'error' in me.data:
        flash('OAuth login is denied!', 'error')
        return redirect(url_for('questions'))
    if 'email' in me.data:
        session['email'] = me.data['email']
        session['fname'] = me.data['given_name']
        session['lname'] = me.data['family_name']
    return redirect(url_for('create_or_login'))


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')


@OA.route('/fb_login')
def fb_login():
    return facebook.authorize(callback=url_for('oauth.fb_authorized',_external=True))


@OA.route('/fb_login/authorized')
def fb_authorized():
    resp = facebook.authorized_response()
    if resp is None:
        flash('OAuth login is denied!', 'error')
        return redirect(url_for('questions'))

    if isinstance(resp, OAuthException):
        flash('OAuth login is denied!', 'error')
        return redirect(url_for('questions'))
    session['fb_token'] = (resp['access_token'], '')
    me = facebook.get('/me')

    if 'email' in me.data:
        session['email'] = me.data['email']
        session['fname'] = me.data['last_name']
        session['lname']  = me.data['first_name']
    return redirect(url_for('create_or_login'))


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('fb_token')

'''
@twitter.tokengetter
def get_twitter_token():
    if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']


@OA.route('/t_login')
def t_login():
    return twitter.authorize(callback=url_for('oauth.t_authorized',_external=True))

@OA.route('/t_login/authorized')
def t_authorized():
    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in.')
    else:
        session['twitter_oauth'] = resp

    return jsonify({'data': resp})


@OA.route('/l_login')
def l_login():
    return linkedin.authorize(callback=url_for('oauth.l_authorized',_external=True))

@OA.route('/l_login/authorized')
def l_authorized():
    resp = linkedin.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
                request.args['error_reason'],
                request.args['error_description']
            )
    session['linkedin_token'] = (resp['access_token'], '')
    me = linkedin.get('people/~')
    return jsonify({'data': resp})

@linkedin.tokengetter
def get_linkedin_oauth_token():
    return session.get('linkedin_token')

def change_linkedin_query(uri, headers, body):
    auth = headers.pop('Authorization')
    headers['x-li-format'] = 'json'
    if auth:
        auth = auth.replace('Bearer', '').strip()
    if '?' in uri:
        uri += '&oauth2_access_token=' + auth
    else:
        uri += '?oauth2_access_token=' + auth
    return uri, headers, body

linkedin.pre_request = change_linkedin_query
'''