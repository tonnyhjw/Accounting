#! -*-coding=utf-8-*-


__author__ = "Huang Jingwen"
from flask_restplus import Api

from views.login import login_required

api = Api(
    title='Feedback Assistant',
    version='1.0',
    description='Documentation of feedback assistant back-end api.',
    # All API metadatas
)
