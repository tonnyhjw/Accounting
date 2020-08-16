#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "gzhuangjingwen"

import os
import base64
from flask_openid import OpenID
from flask import Flask, request, session, redirect, g, jsonify, render_template
from flask import Blueprint
from flask_cors import CORS

from views import *
from views.login import login_required
from utils.helpers import get_logger

# production env log level INFO
log = get_logger(__name__, level=20)

# app = Flask(__name__)
app = Flask(__name__, static_folder="./dist/static", template_folder="./dist")
CORS(app)
api.init_app(app)
app.config['SWAGGER_UI_JSONEDITOR'] = True

# *****尝试blueprint 建立请求********
'''
from views.reply_template import bp_reply_template
app.register_blueprint(bp_reply_template)
'''
# *************
from views.cost import api as cost_ns


blueprint = Blueprint('api', __name__, url_prefix='/api')
api.init_app(blueprint)
api.add_namespace(cost_ns)


#*************************** openid auth ****************************
__dir__ = os.path.dirname(os.path.abspath(__file__))
__tmp__ = os.path.join(__dir__, 'tmp')
oid = OpenID(app, os.path.join(__tmp__, 'openid'), safe_roots=[])

def base64_encode_image(a):
    # base64 encode the input NumPy array
    return base64.b64encode(a).decode("utf-8")

def next_url():
    return request.args.get('next') or request.referrer or '/'

@app.before_request
def before_request():
    uid = session.get('user_id')
    if uid:
        g.user = {
            'name': session.get('user_name'),
            'email': session.get('user_email')
        }
        log.debug("email is : {}".format(g.user['email']))
        return
    g.user = None

#允许跨域访问
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,User-Agent,Access-Control-Allow-Headers,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/api/v1/login')
@oid.loginhandler
def login():
    if g.user is not None:
        return redirect(oid.get_next_url())
    session['next_url'] = next_url()
    return oid.try_login(app.config['NETEASE_OPENID'], ask_for=['email', 'fullname'])

@oid.after_login
def create_or_login(resp):
    # session['openid'] = resp.identity_url

    session['user_id'] = 1 # just put here(For this is a demo)
    session['user_name'] = resp.fullname
    session['user_email'] = resp.email

    next_url = session.pop('next_url', '/')
    return redirect(next_url)

#
# routes
#
@app.route('/api/v1/user')
@login_required
def user():
    return g.user.get('email')

@app.route('/api/v1/islogin')
def is_login():
    user = ''
    if g.user:
        user = g.user.get('name')
    return jsonify({'code':0, 'user':user})

@app.route('/api/v1/vuelogin')
@login_required
def vue_login():
    return redirect('/vue')

@app.route('/api/v1/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    return redirect('/')

@app.route('/')
def index():
    return "Index Page!"

@app.route('/vue')
def vue_index():
    # return "Index Page!"
     return render_template("index.html")

@app.route('/api/v1/hello')
@login_required
def hello():
    return "Hello, {}".format(g.user.get('email'))

@app.route('/about')
def about():
    return "The about page..."

#*************************** openid auth ****************************

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=30000)
