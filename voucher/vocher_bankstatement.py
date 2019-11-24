import os
from datetime import datetime
from pprint import pprint

from voucher import *
from utils import get_logger
from utils.models import BankStatement
from utils.mongoapi import aggregate_data

"""
进项发票凭证生成
"""

log = get_logger(__name__, level=10)

class VoucherInvoiceBankstatement(VoucherBase):
    model_sub_dir = "xlsx_model/记账凭证模板.xlsx"

    def __init__(self, company_name, object_name, begin_y, begin_m, begin_d, end_y, end_m, end_d):
        self.company_name = company_name
        self.object_name = object_name
        self.output_dir = os.path.join(self.output_dir, self.company_name)
        self.begin_date, self.end_date = datetime(begin_y, begin_m, begin_d), datetime(end_y, end_m, end_d)
        self.model = None
        self.output_filename = None

    def load_by_object_name(self):
        """按对方户名导入"""
        match = {"$match": {"company_name": self.company_name, "object_name": self.object_name,
                            "operation_time": {"$gte": self.begin_date, "$lt": self.end_date}}}

        if self.object_name:
            log.debug("loading object:{}".format(self.object_name))
            group = {"$group": {"_id": "$object_name",
                                "object_income": {"$sum": '$income'},
                                "object_outcome": {"$sum": '$outcome'}}}
            self.object_io = aggregate_data(BankStatement, [match, group])
            self.output_filename = "银行凭证-" + self.object_name
            pprint(self.object_io)
        else:
            log.debug("loading other expense data")
            group = {"$group": {"_id": "$abstract",
                                "object_income": {"$sum": '$income'},
                                "object_outcome": {"$sum": '$outcome'}}}
            self.object_io = aggregate_data(BankStatement, [match, group])
            self.output_filename = "银行凭证-其他费用"
            pprint(self.object_io)
        return

    def income(self):
        self.load_model(output_filename=self.output_filename+"-收入")

        return

    def outcome(self):
        self.load_model(output_filename=self.output_filename+"-支出")

        return

    def sum_price(self):
        """填写总收入"""
        pipeline = []
        match = {"$match": {"company_name":self.company_name, "object_name":self.object_name, "invoice_type": "buy",
                            "billing_date": {"$gte": self.begin_date, "$lt": self.end_date}}}
        group = {"$group": {"_id": "$object_name", "total": {"$sum": '$sum_price'}}}
        pipeline.append(match)
        pipeline.append(group)
        # pprint(pipeline)
        self.sum_price_of_object = aggregate_data(Invoice, pipeline)[0]['total']
        log.debug(self.sum_price_of_object)
        self.model.write_cell(6, 4, "库存商品")
        self.model.write_cell(6, 6, self.sum_price_of_object)
        return self.sum_price

    def tax(self):
        """填写应交税费"""
        pipeline = []
        match = {"$match": {"company_name":self.company_name, "object_name":self.object_name, "invoice_type": "buy",
                            "billing_date": {"$gte": self.begin_date, "$lt": self.end_date}}}
        group = {"$group": {"_id": "$object_name", "total": {"$sum": '$tax'}}}
        pipeline.append(match)
        pipeline.append(group)
        # pprint(pipeline)
        self.tax_of_object = aggregate_data(Invoice, pipeline)[0]['total']
        log.debug(self.tax_of_object)
        self.model.write_cell(7, 4, "应交税费")
        self.model.write_cell(7, 5, "应交增值税-进项税")
        self.model.write_cell(7, 6, self.tax_of_object)
        return self.sum_price

    def object_loan(self):
        """填写应收账款"""
        self.model.write_cell(8, 4, "应付账款")
        self.model.write_cell(8, 5, self.object_name)
        self.model.write_cell(8, 7, self.sum_price_of_object+self.tax_of_object)

    def build_vocher(self):
        """"""
        self.load_by_object_name()



if __name__ == '__main__':
    vs = VoucherInvoiceBuy('广州南方化玻医疗器械有限公司', "广州市侨鑫医疗器械科技发展有限公司", 2019, 1, 1, 2019, 10, 31)
    vs.build_vocher()
