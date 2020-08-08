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
from utils.helper import get_logger
from utils.configs import current_cfg

# production env log level INFO
log = get_logger(__name__, level=20)

# app = Flask(__name__)
app = Flask(__name__, static_folder="./dist/static", template_folder="./dist")
CORS(app)
api.init_app(app)
app.config['SWAGGER_UI_JSONEDITOR'] = True
app.config.from_object(current_cfg)

# *****尝试blueprint 建立请求********
'''
from views.reply_template import bp_reply_template
app.register_blueprint(bp_reply_template)
'''
# *************
from views.change_state import api as change_state_ns
from views.feedback_statistics import api as feedback_statistics_ns
from views.keyword import api as keyword_ns
from views.new_game import api as new_game_ns
from views.reply import api as reply_ns
from views.reply_template import api as reply_template_ns
from views.qa_pop_search_words import ns as qa_pop_search_word_ns
from views.feedback_type_stats import api as feedback_type_stats_ns
from views.feedback_qa_handle_stats import api as feedback_qa_handle_stats_ns
from views.feedback_qa_solve_stats import api as feedback_qa_solve_stats_ns
from views.feedback_handle_stats import api as feedback_handle_stats_ns
from views.feedback_solve_stats import api as feedback_solve_stats_ns
from views.feedback_classic import ns as feedback_classic_ns
from views.feedback_keyword_monitor import ns as feedback_keyword_monitor_ns
from views.feedback_keyword_monitor_subscribers import ns as feedback_keyword_monitor_subscribers_ns
from views.feedback_fbstatsbygame import api as feedback_fbstatsbygame_ns
from views.feedback_fbsearchgame import api as feedback_fbsearchgame_ns
from views.feedback_qa import api as feedback_qa_ns
from views.feedback_cancel import api as feedback_cancel_ns
from views.excel import api as excel_ns
from views.exceluuqa import api as exceluuqa_ns

blueprint = Blueprint('api', __name__, url_prefix='/api')
api.init_app(blueprint)
api.add_namespace(change_state_ns)
api.add_namespace(feedback_statistics_ns)
api.add_namespace(keyword_ns)
api.add_namespace(new_game_ns)
api.add_namespace(reply_ns)
api.add_namespace(reply_template_ns)
api.add_namespace(qa_pop_search_word_ns)
api.add_namespace(feedback_type_stats_ns)
api.add_namespace(feedback_qa_handle_stats_ns)
api.add_namespace(feedback_qa_solve_stats_ns)
api.add_namespace(feedback_handle_stats_ns)
api.add_namespace(feedback_solve_stats_ns)
api.add_namespace(feedback_classic_ns)
api.add_namespace(feedback_keyword_monitor_ns)
api.add_namespace(feedback_keyword_monitor_subscribers_ns)
api.add_namespace(feedback_fbstatsbygame_ns)
api.add_namespace(feedback_fbsearchgame_ns)
api.add_namespace(feedback_qa_ns)
api.add_namespace(feedback_cancel_ns)
api.add_namespace(excel_ns)
api.add_namespace(exceluuqa_ns)
app.register_blueprint(blueprint)

# url
# api.add_resource(NewGameViewSet, '/api/v1/feedback/newgames')
# api.add_resource(ReplyViewSet, '/api/v1/feedback/reply')
# api.add_resource(ChangeStateViewSet, '/api/v1/feedback/changestate')
# api.add_resource(Keyword, '/api/v1/feedback/keyword')
# api.add_resource(FeedbackStatistics, '/api/v1/feedback/fbstatistics')
# api.add_resource(ReplyTemplate, '/api/v1/feedback/replytemplate')
# api.add_resource(ClassicProblemViewSet, '/api/v1/feedback/classicproblems')
# api.add_resource(QaPopSearchWords, '/api/v1/feedback/qapopsearchwords')
# api.add_resource(FeedbackTypeStats, '/api/v1/feedback/fbtypestats')
# api.add_resource(FeedbackQaHandleStats, '/api/v1/feedback/fbqahandlestats') # TODO: Replace by /fbqasolvestats. Subject to DELETE
# api.add_resource(FeedbackQaSolveStats, '/api/v1/feedback/fbqasolvestats')
# api.add_resource(FeedbackHandleStats, '/api/v1/feedback/fbhandlestats')
# api.add_resource(FeedbackSolveStats, '/api/v1/feedback/fbsolvestats')


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
    app.run(debug=True, host="0.0.0.0", port=30666)
