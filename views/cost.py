#! -*-coding=utf-8-*-

__author__ = "Huang Jingwen"

from flask import jsonify, send_from_directory
from flask_restplus import Resource, Namespace
import os
from pprint import pprint


from utils.helpers import get_logger, exe_time
from utils.mongoapi import aggregate_data, insert_data
from utils.configs import PROJECT_ROOT
from views import api


log = get_logger(name=__name__)
api = api.namespace('v1/accounting/cost', description='keyword restful api')

parser = api.parser()
parser.add_argument('start_offset', default=7, type=int)
parser.add_argument('end_offset', default=0, type=int)
parser.add_argument('start_time', default=None, type=str)
parser.add_argument('end_time', default=None, type=str)
parser.add_argument('platform', type=str, required=True)
parser.add_argument('keyword', default='', type=str)
parser.add_argument('by_QA', default=True, type=bool)

@api.route('/')
class Cost(Resource):
    @api.expect(parser)
    # @login_required
    def get(self):
        args = parser.parse_args()
        log.debug("GET param: {}".format(args))
        collection = feedback_db[args['platform']]
        filter_activated = self.filters[args['platform']](start_offset=args['start_offset'],
                                                          end_offset=args['end_offset'],
                                                          start_time=args['start_time'],
                                                          end_time=args['end_time'])

        data = list(aggregate_data(filter=filter_activated.excel(regex=args['keyword'], by_QA=args['by_QA']), collection=collection))
        directory = os.path.join(PROJECT_ROOT, "tmp/excel")
        filename = "feedback.xlsx"
        return send_from_directory(directory, filename, as_attachment=True)
