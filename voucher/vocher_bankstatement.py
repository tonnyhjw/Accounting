import os
from datetime import datetime
from pprint import pprint
# from typing import io

from voucher import *
from utils import get_logger
from utils.models import BankStatement
from utils.mongoapi import aggregate_data

"""
进项发票凭证生成
"""

log = get_logger(__name__, level=10)

class VoucherBankstatement(VoucherBase):

    def __init__(self, company_name, object_name, begin_y, begin_m, begin_d, end_y, end_m, end_d, num_in, num_out):
        super(VoucherBankstatement, self).__init__()
        self.category = "银行凭证"
        self.company_name = company_name
        self.object_name = object_name
        self.output_dir = os.path.join(self.output_dir, self.company_name)
        self.begin_date, self.end_date = datetime(begin_y, begin_m, begin_d), datetime(end_y, end_m, end_d)
        self.model = None
        self.output_filename = None
        self.num_in, self.num_out = num_in, num_out

    def load_by_object_name(self):
        """按对方户名导入"""
        match = {"$match": {"company_name": self.company_name, "object_name": self.object_name,
                            "operation_time": {"$gte": self.begin_date, "$lte": self.end_date}}}

        if self.object_name:
            log.debug("loading object:{}".format(self.object_name))
            group = {"$group": {"_id": "$object_name",
                                "object_income": {"$sum": '$income'},
                                "object_outcome": {"$sum": '$outcome'}}}
            self.object_io = aggregate_data(BankStatement, [match])
            # self.object_io = aggregate_data(BankStatement, [match, group])[0]
            self.output_filename = "银行凭证-" + self.object_name
            self.wirte_specific(specific=self.object_name)
        else:
            log.debug("读取无对方名的银行对账单记录")
            group = {"$group": {"_id": "$abstract",
                                "object_income": {"$sum": '$income'},
                                "object_outcome": {"$sum": '$outcome'}}}
            self.object_io = aggregate_data(BankStatement, [match, group])
            self.output_filename = "银行凭证-其他费用"
            self.wirte_specific(specific="其他费用")
        return

    def income(self):
        self.reset_db_object()
        """ self.object_io = 
        [{'_id': ObjectId('5e6cc9cdebb2bf0764fb920d'),
          'abstract': '电汇',
          'balance': 478528.47,
          'bank': '广州银行',
          'company_name': '广州南方化玻医疗器械有限公司',
          'income': 3000.0,
          'insert_time': datetime.datetime(2020, 3, 14, 20, 10, 53, 650000),
          'object_account': '\xa080020000006948766',
          'object_name': '四会市人民医院',
          'operation_time': datetime.datetime(2020, 1, 31, 0, 0),
          'outcome': 0.0},
         {'_id': ObjectId('5e6cc9cdebb2bf0764fb920e'),
          'abstract': '电汇',
          'balance': 480478.47,
          'bank': '广州银行',
          'company_name': '广州南方化玻医疗器械有限公司',
          'income': 1950.0,
          'insert_time': datetime.datetime(2020, 3, 14, 20, 10, 53, 653000),
          'object_account': '\xa080020000006948766',
          'object_name': '四会市人民医院',
          'operation_time': datetime.datetime(2020, 1, 31, 0, 0),
          'outcome': 0.0}]
        """
        if self.object_name and self.object_io[0]['income']:
            self.category += "-收入"
            self.load_model(output_filename=self.output_filename+"-收入")

            # self.db_object["row_1"][2] = "收款"
            # self.db_object["row_1"][4] = "银行存款*"
            # self.db_object["row_1"][6] = self.object_io['object_income']

            sum_income = 0
            for i, io in enumerate(self.object_io):
                y, m, d = io['operation_time'].year, io['operation_time'].month, io['operation_time'].day
                self.db_object["row_{}".format(i+1)][2] = "收款-{}-{}-{}".format(y, m, d)
                self.db_object["row_{}".format(i+1)][4] = "银行存款*"
                self.db_object["row_{}".format(i+1)][6] = io['income']
                sum_income += io['income']

            self.db_object["row_{}".format(len(self.object_io)+1)][2] = "收款"
            self.db_object["row_{}".format(len(self.object_io)+1)][4] = "应收账款"
            self.db_object["row_{}".format(len(self.object_io)+1)][5] = self.object_io[0]['object_name']
            self.db_object["row_{}".format(len(self.object_io)+1)][7] = sum_income

            self.write_company_name()
            self.write_end_date()
            self.wirte_specific(self.object_name)
            self.transfer_method(method=0)
            self.vocher_num(self.num_in)
            self.num_in += 1
            # self.output()
            self.insert_db()

            log.debug("write object_income {} to voucher".format(sum_income))
        # elif isinstance(self.object_io, list):
        #     log.debug('this object is other expense')
        else:
            log.debug("this object is other expense, skip income() process.")

        self.category = "银行凭证"
        return

    def outcome(self):
        self.reset_db_object()
        if self.object_name:
            if not self.object_io[0]['outcome']:
                log.info("skip! {} bank reocrd outcome is {}".format(self.object_name, self.object_io[0]['outcome']))
                return
            self.category += "-支出"
            self.load_model(output_filename=self.output_filename+"-支出")

            # self.db_object["row_2"][2] = "付款"
            # self.db_object["row_2"][4] = "银行存款*"
            # self.db_object["row_2"][7] = self.object_io['object_outcome']

            sum_outcome = 0
            for i, io in enumerate(self.object_io):
                y, m, d = io['operation_time'].year, io['operation_time'].month, io['operation_time'].day
                self.db_object["row_{}".format(i + 2)][2] = "付款-{}-{}-{}".format(y, m, d)
                self.db_object["row_{}".format(i + 2)][4] = "银行存款*"
                self.db_object["row_{}".format(i + 2)][7] = io['outcome']
                sum_outcome += io['outcome']

            self.db_object["row_1"][2] = "收款"
            self.db_object["row_1"][4] = "应付账款"
            self.db_object["row_1"][5] = self.object_io[0]['object_name']
            self.db_object["row_1"][6] = sum_outcome

            self.write_company_name()
            self.write_end_date()
            self.wirte_specific(self.object_name)
            self.transfer_method(method=1)
            self.vocher_num(self.num_out)
            self.num_out += 1
            # self.output()
            self.insert_db()

            log.debug("write object_outcome {} to voucher".format(sum_outcome))
        elif not self.object_name and isinstance(self.object_io, list):
            log.debug('this object is other expense')
            self.other_expense()
        else:
            log.debug("object_outcome is {}".format(self.object_io[0]['outcome']))
            raise RuntimeError("银行对账单记录无对方名称，且不是list类型")

        self.category = "银行凭证"
        return

    def other_expense(self):
        self.reset_db_object()

        for io in self.object_io:
            self.load_model(output_filename=self.output_filename + "-" + io['_id'])
            if io['_id'] == '手续费':
                self.category += "-手续费"

                self.db_object["row_1"][2] = "手续费"
                self.db_object["row_2"][2] = "手续费"
                self.db_object["row_1"][4] = "财务费用"
                self.db_object["row_1"][5] = "手续费"
            elif io['_id'] == '话费':
                self.category += "-电话费"

                self.db_object["row_1"][2] = "话费"
                self.db_object["row_2"][2] = "话费"
                self.db_object["row_1"][4] = "管理费用"
                self.db_object["row_1"][5] = "办公费"
            elif io['_id'] == '社保费':
                self.category += "-社保费"

                self.db_object["row_1"][2] = "社保费"
                self.db_object["row_2"][2] = "社保费"
                self.db_object["row_1"][4] = "管理费用"
                self.db_object["row_1"][5] = "社保费"
            elif io['_id'] == 'TG':
                self.category += "-TG"

                self.db_object["row_1"][2] = "TG"
                self.db_object["row_2"][2] = "TG"
                self.db_object["row_1"][4] = "应交税费"
                self.db_object["row_1"][5] = "总应交税费"
            elif io['_id'] == '现金':
                self.category += "-现金"

                self.db_object["row_1"][2] = "提现"
                self.db_object["row_2"][2] = "提现"
                self.db_object["row_1"][4] = "现金"
            elif io['_id'] == '存息':
                self.category += "-存息"

                self.db_object["row_1"][2] = "存息"
                self.db_object["row_2"][2] = "存息"
                self.db_object["row_1"][4] = "账务费用"
                self.db_object["row_1"][5] = "利息支出"
            else:
                log.debug("not defined other expense")
                raise ValueError("Unrecognized abstract: {}".format(io['_id']))


            self.model.write_cell(6, 6, io['object_outcome'])
            self.model.write_cell(7, 4, "银行存款")
            self.model.write_cell(7, 7, io['object_outcome'])

            self.db_object["row_1"][6] = io['object_outcome']
            self.db_object["row_1"][7] = io['object_income']
            self.db_object["row_2"][4] = "银行存款*"
            self.db_object["row_2"][6] = io['object_income']
            self.db_object["row_2"][7] = io['object_outcome']

            self.write_company_name()
            self.write_end_date()
            self.wirte_specific("其他费用")
            self.transfer_method(method=1)
            self.vocher_num(self.num_out)
            self.num_out += 1
            # self.output()
            self.insert_db()
            self.category = "银行凭证"

            log.debug("built voucher of {}".format(io['_id']))

        # self.category = "银行凭证"
        return

    def build_vocher(self):
        """创建数据库中的凭证"""
        self.load_by_object_name()
        self.income()
        self.outcome()





if __name__ == '__main__':
    vs = VoucherInvoiceBuy('广州南方化玻医疗器械有限公司', "广州市侨鑫医疗器械科技发展有限公司", 2019, 1, 1, 2019, 10, 31)
    vs.build_vocher()
