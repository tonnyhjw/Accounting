import os
from datetime import datetime
from pprint import pprint
from typing import io

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
            self.object_io = aggregate_data(BankStatement, [match, group])[0]
            self.output_filename = "银行凭证-" + self.object_name
            # pprint(self.object_io)
        else:
            log.debug("loading other expense data")
            group = {"$group": {"_id": "$abstract",
                                "object_income": {"$sum": '$income'},
                                "object_outcome": {"$sum": '$outcome'}}}
            self.object_io = aggregate_data(BankStatement, [match, group])
            self.output_filename = "银行凭证-其他费用"
            # pprint(self.object_io)
        return

    def income(self):
        if self.object_name and self.object_io['object_income']:
            self.load_model(output_filename=self.output_filename+"-收入")
            self.model.write_cell(6, 2, "收款")
            self.model.write_cell(6, 4, "银行存款")
            # self.model.write_cell(6, 5, "收入")
            self.model.write_cell(6, 6, self.object_io['object_income'])
            self.model.write_cell(7, 2, "收款")
            self.model.write_cell(7, 4, "应收账款")
            self.model.write_cell(7, 5, self.object_io['_id'])
            self.model.write_cell(7, 7, self.object_io['object_income'])
            self.write_company_name()
            self.write_end_date()
            self.output()
            log.debug("write object_income {} to voucher".format(self.object_io['object_income']))
        elif isinstance(self.object_io, list):
            log.debug('this object is other expense')
        else:
            log.debug("object_income is {}".format(self.object_io['object_income']))

        return

    def outcome(self):
        if self.object_name and self.object_io['object_outcome']:
            self.load_model(output_filename=self.output_filename+"-支出")
            self.model.write_cell(7, 2, "付款")
            self.model.write_cell(7, 4, "银行存款")
            # self.model.write_cell(7, 5, "支出")
            self.model.write_cell(7, 7, self.object_io['object_outcome'])
            self.model.write_cell(6, 2, "付款")
            self.model.write_cell(6, 4, "应付账款")
            self.model.write_cell(6, 5, self.object_io['_id'])
            self.model.write_cell(6, 6, self.object_io['object_outcome'])
            self.write_company_name()
            self.write_end_date()
            self.output()
            log.debug("write object_outcome {} to voucher".format(self.object_io['object_outcome']))
        elif not self.object_name and isinstance(self.object_io, list):
            log.debug('this object is other expense')
            self.other_expense()
        else:
            log.debug("object_outcome is {}".format(self.object_io['object_outcome']))

        return

    def other_expense(self):
        for io in self.object_io:
            self.load_model(output_filename=self.output_filename + "-" + io['_id'])
            if io['_id'] == '手续费':
                self.model.write_cell(6, 2, "支付手续费")
                self.model.write_cell(7, 2, "支付手续费")
                self.model.write_cell(6, 4, "财务费用")
                self.model.write_cell(6, 5, "手续费")
            elif io['_id'] == '电话费':
                self.model.write_cell(6, 2, "付电话费")
                self.model.write_cell(7, 2, "付电话费")
                self.model.write_cell(6, 4, "管理费用")
                self.model.write_cell(6, 5, "办公费")
            elif io['_id'] == '社保费':
                self.model.write_cell(6, 2, "交社保费")
                self.model.write_cell(7, 2, "交社保费")
                self.model.write_cell(6, 4, "管理费用")
                self.model.write_cell(6, 5, "社保费")
            elif io['_id'] == 'TG':
                self.model.write_cell(6, 2, "交税")
                self.model.write_cell(7, 2, "交税")
                self.model.write_cell(6, 4, "应交税费")
            elif io['_id'] == '现金':
                self.model.write_cell(6, 2, "提现")
                self.model.write_cell(7, 2, "提现")
                self.model.write_cell(6, 4, "现金")
            else:
                log.debug("not defined other expense")

            self.model.write_cell(6, 6, io['object_outcome'])

            self.model.write_cell(7, 4, "银行存款")
            # self.model.write_cell(7, 5, "支出")
            self.model.write_cell(7, 7, io['object_outcome'])
            self.write_company_name()
            self.write_end_date()
            self.output()
            log.debug("built voucher of {}".format(io['_id']))
        return

    def build_vocher(self):
        """"""
        self.load_by_object_name()
        self.income()
        self.outcome()





if __name__ == '__main__':
    vs = VoucherInvoiceBuy('广州南方化玻医疗器械有限公司', "广州市侨鑫医疗器械科技发展有限公司", 2019, 1, 1, 2019, 10, 31)
    vs.build_vocher()
