"""
科目余额表
"""

from pprint import pprint

from utils import *
from utils.mongoapi import aggregate_data

log = get_logger(__name__, level=10)

class SubjectBalance():
    empty_row = [""]*8
    subject_lv1_idx = 4
    subject_lv2_idx = 5
    debit_idx = -2
    credit_idx = -1

    def __init__(self, company_name, year, month):
        self.company_name, self.year, self.month = company_name, year, month
        self.vouchers = []

    def query_vouchers(self):
        """查询本期所有凭证"""
        project = {
            "$project": {
                "_id": "$$REMOVE",
                "year": {"$year": "$date"},
                "month": {"$month": "$date"},
                "day": {"$dayOfMonth": "$date"},
                "specific":1, "company_name":1,
                "row_1":1, "row_2":1, "row_3":1, "row_4":1, "row_5":1, "row_6":1
            }
        }
        match = {"$match": {"month": self.month, "year": self.year}}
        pipeline = [project, match]
        self.vouchers = aggregate_data(Voucher, pipeline)
        log.debug("got {} vouchers".format(len(self.vouchers)))
        return

    def iter_balance(self):
        """返回凭证每个科目余额"""
        if not self.vouchers:
            log.critical("Vouchers not found! ")
            return

        for voucher in self.vouchers:
            for subject in voucher.values():
                if isinstance(subject, list) and subject != self.empty_row:

                    yield {
                        "subject_lv1": subject[self.subject_lv1_idx],
                        "subject_lv2": subject[self.subject_lv2_idx],
                        "cur_amount_debit": subject[self.debit_idx],
                        "cur_amount_credit": subject[self.credit_idx]
                    }


    def query_previous_balance(self):
        """"""
        log.info("this is {}".format(__name__))


    def setup_subject_balance(self):
        """"""
        pass

    def inser_db(self):
        """将科目余额存入数据库"""
        pass

    def output(self):
        """输出科目余额表excel"""
        pass


if __name__ == '__main__':
    sb = SubjectBalance(company_name="广州南方化玻医疗器械有限公司", year=2019, month=12)
    sb.query_vouchers()
    for i in sb.iter_balance():
        print(i)


