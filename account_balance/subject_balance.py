"""
科目余额表
"""

from utils import *
from utils.mongoapi import aggregate_data


class SubjectBalance():
    company_name = None
    subject_lv1 = ""
    subject_lv2 = ""
    subject_lv3 = ""

    def _init_balance(self):
        pipeline = []
        aggregate_data(Voucher, pipeline)
        self.init_balance = ""
        return