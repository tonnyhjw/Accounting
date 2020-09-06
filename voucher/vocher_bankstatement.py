import os
import datetime
from dateutil.relativedelta import relativedelta
from playhouse.shortcuts import model_to_dict
from pprint import pprint
# from typing import io

from voucher import *
from utils import get_logger
from utils.models import BankStatement
from utils.models_sql import BankStatement as BankStatementSql, VoucherRow
from utils.mongoapi import aggregate_data

"""
进项发票凭证生成
"""

log = get_logger(__name__, level=10)

class VoucherBankstatement(VoucherBase):

    def __init__(self, company_name, object_name, year, month, num_in, num_out):
        super(VoucherBankstatement, self).__init__()
        self.category = "银行凭证"
        self.company_name = company_name
        self.object_name = object_name
        self.output_dir = os.path.join(self.output_dir, self.company_name)
        self.begin_date = datetime.date(year=year, month=month, day=1)
        self.end_date = self.begin_date + relativedelta(months=+1, seconds=-1)
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

    def load_by_object_name_sql(self):
        """按对方户名导入sql"""
        if self.object_name:
            log.debug("loading object:{}".format(self.object_name))

            bank_statements = BankStatementSql.select().where(
                (BankStatementSql.company_name == self.company_name) &
                (BankStatementSql.object_name == self.object_name) &
                (BankStatementSql.operation_time.between(self.begin_date, self.end_date)))
            self.object_io = list(bank_statements)

            self.output_filename = "银行凭证-" + self.object_name
            self.wirte_specific(specific=self.object_name)
        else:
            log.debug("读取无对方名的银行对账单记录")
            self.object_io = BankStatementSql.select().where(
                (BankStatementSql.company_name == self.company_name) &
                (BankStatementSql.object_name == self.object_name) &
                (BankStatementSql.operation_time.between(self.begin_date, self.end_date))
            ).group_by(BankStatementSql.abstract)

            self.output_filename = "银行凭证-其他费用"
            self.wirte_specific(specific="其他费用")


        return

    def income(self):
        self.reset_db_object(db_type='mongo')
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

    def income_sql(self):
        self.reset_db_object()
        if self.object_name:
            self.category += "-收入"
            sum_income = 0
            for i, io in enumerate(self.object_io):
                # 若存在收入才开始制作收入凭证
                if io.income:
                    y, m, d = io.operation_time.year, io.operation_time.month, io.operation_time.day
                    self.db_object[f"row_{i + 1}"] = VoucherRow.create(index_2=f"收款-{y}-{m}-{d}",
                                                                       index_4="银行存款*",
                                                                       index_6=io.income)
                    sum_income += io.income
            # 若收入总和不为0才开始构建应收账款，避免出现应收为0的凭证。
            if sum_income:
                self.db_object[f"row_{len(self.object_io) + 1}"] = VoucherRow.create(index_2="收款",
                                                                                     index_4="应收账款",
                                                                                     index_5=self.object_name,
                                                                                     index_7=sum_income)
            else:
                log.info(f'total income of {self.object_name} is {sum_income}, skip!')
                return

            self.write_company_name()
            self.write_end_date()
            self.wirte_specific(self.object_name)
            self.transfer_method(method=0)
            self.vocher_num(self.num_in)
            self.num_in += 1
            self.insert_sql()
            log.debug("write object_income {} to voucher".format(sum_income))
        else:
            log.debug("this object is other expense, skip income_sql() process.")

        self.category = "银行凭证"
        return

    def outcome(self):
        self.reset_db_object(db_type='mongo')
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
                log.info("i:{}, io:{}".format(i, io))
                y, m, d = io['operation_time'].year, io['operation_time'].month, io['operation_time'].day
                self.db_object["row_{}".format(i + 2)][2] = "付款-{}-{}-{}".format(y, m, d)
                self.db_object["row_{}".format(i + 2)][4] = "银行存款*"
                self.db_object["row_{}".format(i + 2)][7] = io['outcome']
                sum_outcome += io['outcome']

            self.db_object["row_1"][2] = "付款"
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

    def outcome_sql(self):
        self.reset_db_object()
        if self.object_name:
            self.category += "-支出"
            sum_outcome = 0
            for i, io in enumerate(self.object_io):
                if io.outcome:
                    y, m, d = io.operation_time.year, io.operation_time.month, io.operation_time.day
                    self.db_object[f"row_{i + 2}"] = VoucherRow.create(index_2=f"付款-{y}-{m}-{d}",
                                                                       index_4="银行存款*",
                                                                       index_7=io.outcome)
                    sum_outcome += io.outcome
            if sum_outcome:
                self.db_object["row_1"] = VoucherRow.create(index_2="付款",
                                                            index_4="应付账款",
                                                            index_5=self.object_name,
                                                            index_6=sum_outcome)
            else:
                log.info(f'total income of {self.object_name} is {sum_outcome}, skip!')
                return

            self.write_company_name()
            self.write_end_date()
            self.wirte_specific(self.object_name)
            self.transfer_method(method=1)
            self.vocher_num(self.num_out)
            self.num_out += 1
            self.insert_sql()
            log.debug(f"write object_outcome {sum_outcome} to voucher")
        elif not self.object_name:
            log.debug('this object is other expense, skip outcome_sql and launch other_expense_sql')
            self.other_expense_sql()
        else:
            log.debug(f"object_outcome is {self.object_io[0].outcome}")
            raise RuntimeError("银行对账单记录无对方名称，且不是list类型")

        self.category = "银行凭证"
        return

    def other_expense(self):

        for io in self.object_io:
            self.reset_db_object(db_type='mongo')
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

    def other_expense_sql(self):
        # todo
        for io in self.object_io:
            log.debug(model_to_dict(io))
            self.reset_db_object()
            row_1 = {'index_6': io.outcome, 'index_7': io.income}
            row_2 = {'index_6': io.income, 'index_7': io.outcome,
                     'index_4': "银行存款*"}

            if io.abstract == '手续费':
                self.category += "-手续费"

                row_1['index_2'] = "手续费"
                row_2['index_2'] = "手续费"
                row_1['index_4'] = "财务费用"
                row_1['index_5'] = "手续费"
            elif io.abstract == '话费':
                self.category += "-电话费"

                row_1['index_2'] = "话费"
                row_2['index_2'] = "话费"
                row_1['index_4'] = "管理费用"
                row_1['index_5'] = "办公费"
            elif io.abstract == '社保费':
                self.category += "-社保费"

                row_1['index_2'] = "社保费"
                row_2['index_2'] = "社保费"
                row_1['index_4'] = "管理费用"
                row_1['index_5'] = "社保费"
            elif io.abstract == 'TG':
                self.category += "-TG"

                row_1['index_2'] = "TG"
                row_2['index_2'] = "TG"
                row_1['index_4'] = "应交税费"
                row_1['index_5'] = "总应交税费"
            elif io.abstract == '现金':
                self.category += "-现金"

                row_1['index_2'] = "提现"
                row_2['index_2'] = "提现"
                row_1['index_4'] = "现金"
            elif io.abstract == '存息':
                self.category += "-存息"

                row_1['index_2'] = "存息"
                row_2['index_2'] = "存息"
                row_1['index_4'] = "账务费用"
                row_1['index_5'] = "利息支出"
            else:
                log.debug("not defined other expense")
                raise ValueError("Unrecognized abstract: {}".format(io.abstract))

            self.db_object["row_1"] = VoucherRow.create(**row_1)
            self.db_object["row_2"] = VoucherRow.create(**row_2)

            self.write_company_name()
            self.write_end_date()
            self.wirte_specific("其他费用")
            self.transfer_method(method=1)
            self.vocher_num(self.num_out)
            self.num_out += 1
            self.insert_sql()
            self.category = "银行凭证"

            log.debug("built voucher of {}".format(io.abstract))

        return

    def build_vocher(self):
        """创建数据库中的凭证"""
        # mongo
        self.load_by_object_name()
        self.income()
        self.outcome()

    def build_voucher_sql(self):
        # sql
        self.load_by_object_name_sql()
        self.income_sql()
        self.outcome_sql()








if __name__ == '__main__':
    vs = VoucherBankstatement('广州南方化玻医疗器械有限公司', "广州市侨鑫医疗器械科技发展有限公司", 2019, 1, 1, 1)
    vs.build_vocher()
