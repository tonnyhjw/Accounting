#! -*-coding=utf-8-*-

__author__ = "Huang Jingwen"

from flask import jsonify, send_from_directory
from flask_restplus import Resource, Namespace
import os
from pprint import pprint


from utils.helpers import get_logger, exe_time
from utils.mongoapi import aggregate_data, insert_data
from utils.configs import PROJECT_ROOT
from scrips.cost_scrip import cost_sql
from views import api


log = get_logger(name=__name__)
api = api.namespace('v1/accounting/cost', description='keyword restful api')

parser = api.parser()
parser.add_argument('company_name', type=str, required=True)
parser.add_argument('year', type=int, required=True)
parser.add_argument('month', type=int, required=True)
parser.add_argument('range_btn', default=0, type=float)
parser.add_argument('range_top', default=1, type=float)

@api.route('/')
class Cost(Resource):

    @api.expect(parser)
    def get(self):
        args = parser.parse_args()
        log.debug("GET param: {}".format(args))
        ret = cost_sql(**args)
        return ret

    @api.expect(parser)
    def post(self):

        return jsonify({'method': 'POST'})

@api.route('/download/')
class CostDownload(Resource):

    @api.expect(parser)
    def get(self):
        directory = os.path.join(PROJECT_ROOT, 'output')
        return send_from_directory(directory, 'cost.xls', as_attachment=True)