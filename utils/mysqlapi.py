import os
from xlrd.xldate import xldate_as_datetime
from datetime import datetime
import traceback
from playhouse.shortcuts import model_to_dict

from utils import *

log = get_logger(__name__, level=10)

def insert_documents(collection, data=[]):
    try:
        collection.objects.insert(data)
    except Exception as e:
        print(e)

    return


class BankStatementApi():
    def __init__(self, company):
        self.company = company
        self.bank_infos = Bank.select()
        self.project_root = PROJECT_ROOT

    def insert_all(self):
        for bank_info in self.bank_infos:
            bank_xlsx_dir = os.path.join(self.project_root, bank_info.xlsx_dir)
            for filename in os.listdir(bank_xlsx_dir):
                filepath = os.path.join(bank_xlsx_dir, filename)
                log.debug(filepath)
                xl = Xls(filepath)
                xl_content = xl.contents(row_start=bank_info.starting_row, end_before_last_row=bank_info.ending_row)
                # self.insert_one_xlsx(xl_content, bank_info)
                try:
                    self.insert_one_xlsx(xl_content, bank_info)
                except Exception as e:
                    log.critical("error occur :{}".format(e))
                    continue

    def insert_one_xlsx(self, xl_contents, bank_info):
        for row in xl_contents:
            log.debug(row)
            if row[0] == '交易时间':
                continue
            outcome = 0. if not row[bank_info.outcome_col] else row[bank_info.outcome_col]
            income = 0. if not row[bank_info.income_col] else row[bank_info.income_col]
            operation_time = self.time_fmt(row[bank_info.operation_time_col])

            log.debug(f"outcome: {outcome} outtype: {type(outcome)}  income:{income} intype: {type(income)}"
                      f" operation_time: {operation_time}  org_operation_time: {row[bank_info.operation_time_col]}")

            BankStatement.create(company_name=self.company, object_account=row[bank_info.object_account_col],
                                 object_name=row[bank_info.object_name_col].strip(),
                                 outcome=outcome, income=income, balance=row[bank_info.balance_col],
                                 abstract=row[bank_info.abstract_col], bank=bank_info.bankname, insert_time=datetime.now(), operation_time=operation_time)
        return

    @staticmethod
    def time_fmt(input_time):
        if isinstance(input_time, float):
            return xldate_as_datetime(input_time, 0)
        elif isinstance(input_time, str):
            return datetime.strptime(input_time, "%Y%m%d %H:%M:%S")

    def delete_by_operation_time(self, begin_date, end_date):
        b = BankStatement.delete().where((BankStatement.company_name == self.company) &
                                     (BankStatement.operation_time >= begin_date) &
                                     (BankStatement.operation_time <= end_date)).execute()
        log.info(f'delete {b} lines of bank statements.')
        return b



class InvoiceBaseApi():
    input_dir = None
    row_start = 0
    end_before_last_row = 1

    def __init__(self, company_name):
        self.company_name = company_name


    def insert_all(self):
        if not self.input_dir:
            log.critical("please define input_dir")
            return

        invoice_xlsx_dir = os.path.join(PROJECT_ROOT, self.input_dir)
        for filename in os.listdir(invoice_xlsx_dir):
            filepath = os.path.join(invoice_xlsx_dir, filename)
            log.debug(filepath)
            xl = self.read_excel(filepath)
            xl_content = xl.contents(row_start=self.row_start, end_before_last_row=self.end_before_last_row)

            try:
                self.insert_one_xlsx(xl_content)
            except Exception as e:
                log.critical("error occur: {}".format(e))
                continue

    def insert_one_xlsx(self, xl_contents):
        log.info("Not defined")
        return

    @staticmethod
    def time_fmt(input_time):
        if isinstance(input_time, str):
            return datetime.strptime(input_time, "%Y-%m-%d")

    def read_excel(self, filepath):
        return Xlsx(filepath)


class InvoiceSaleApi(InvoiceBaseApi):
    invoice_code = 0  # 发票代码
    invoice_num = 1  # 发票号码
    object_name = 2  # 购方企业名称
    object_tax_num = 3  # 购方税号
    bank_account = 4  # 银行账号
    billing_date = 6  # 开票日期
    merchandise_name = 9  # 商品名称
    merchandise_amount = 12  # 数量
    unit_price = 13  # 单价
    sum_price = 14  # 金额
    tax_rate = 15  # 税率
    tax = 16  # 税额
    tax_category_code = 17  # 税收分类编码
    input_dir = "input/invoice/sale"
    invoice_type = "sale"
    row_start = 7
    end_before_last_row = 2

    def insert_one_xlsx(self, xl_contents):
        previous_row = []
        for row in xl_contents:
            if row[self.merchandise_name] == '小计':
                log.debug("this line is 小计")
                continue

            log.debug("p row :{}".format(previous_row))
            if row[self.invoice_code] and row[self.object_name] and row[self.billing_date]:
                previous_row = row
            else:
                previous_row = previous_row[:self.merchandise_name] + row[self.merchandise_name:]
            log.debug("n row :{}".format(previous_row))

            billing_date = self.time_fmt(previous_row[self.billing_date])
            merchandise_amount = int(previous_row[self.merchandise_amount]) if previous_row[self.merchandise_amount] else 0
            unit_price = float(previous_row[self.unit_price]) if previous_row[self.unit_price] else 0
            sum_price = float(previous_row[self.sum_price]) if previous_row[self.sum_price] else 0
            tax = float(previous_row[self.tax]) if previous_row[self.tax] else 0

            Invoice.create(company_name=self.company_name, invoice_code=previous_row[self.invoice_code],
                           invoice_num=previous_row[self.invoice_num],
                           object_name=previous_row[self.object_name], object_tax_num=previous_row[self.object_tax_num],
                           bank_account=previous_row[self.bank_account], billing_date=billing_date,
                           merchandise_name=previous_row[self.merchandise_name],
                           merchandise_amount=merchandise_amount, unit_price=unit_price,
                           sum_price=sum_price, tax_rate=tax/sum_price, tax=tax,
                           tax_category_code=previous_row[self.tax_category_code], invoice_type=self.invoice_type)
        return


    def delete_by_billing_date(self, begin_date, end_date):
        invoices = Invoice.delete().where((Invoice.company_name == self.company_name) &
                                          (Invoice.billing_date >= begin_date) &
                                          (Invoice.billing_date <= end_date)).execute()
        log.info(f'delete {invoices} lines of sale invoice.')
        return

class InvoiceBuyApi(InvoiceBaseApi):
    invoice_code = 1  # 发票代码
    invoice_num = 2  # 发票号码
    object_name = 5  # 销方企业名称
    object_tax_num = 4  # 购方税号
    billing_date = 3  # 开票日期
    select_date = 9   # 勾选日期
    belong_date = (1, 7) # 所属日期
    sum_price = 6  # 金额
    # tax_rate = 15  # 税率
    tax = 7  # 税额
    # tax_category_code = 17  # 税收分类编码
    input_dir = "input/invoice/buy"
    invoice_type = "buy"
    row_start = 3
    end_before_last_row = 0

    def insert_one_xlsx(self, xl_contents):

        belong_date = datetime.strptime(self.xls.sheet_r.row_values(self.belong_date[0])[self.belong_date[1]]+"28", "%Y%m%d")
        log.debug("belong date: {}".format(belong_date))
        for row in xl_contents:
            log.debug("row :{}".format(row))

            billing_date = self.time_fmt(row[self.billing_date])
            select_date = self.time_fmt(row[self.select_date])
            sum_price = float(row[self.sum_price]) if row[self.sum_price] else 0
            tax = float(row[self.tax]) if row[self.tax] else 0

            Invoice.create(company_name=self.company_name, invoice_code=row[self.invoice_code], invoice_num=row[self.invoice_num],
                    object_name=row[self.object_name], object_tax_num=row[self.object_tax_num], billing_date=billing_date,
                    sum_price=sum_price, tax_rate=tax/sum_price, tax=tax, invoice_type=self.invoice_type,
                    belong_date=belong_date, select_date=select_date)
        return

    def read_excel(self, filepath):
        self.xls = Xls(filepath)
        return self.xls

    def delete_by_belong_date(self, begin_date, end_date):
        invoices = Invoice.delete().where((Invoice.company_name == self.company_name) &
                                          (Invoice.belong_date >= begin_date) &
                                          (Invoice.belong_date <= end_date)).execute()
        log.info(f'delete {invoices} lines of buy invoice.')
        return invoices

class InitialOpenningBalanceApi():
    """
    期初余额API
    """

    input_dir = "input/initial_openning_balance"
    subject_col = 2                             # 科目所在列
    code_col = 1                                # 科目代码所在列
    cur_balance_debit = 10
    cur_balance_credit = 11

    def __init__(self, company_name, year, month):
        self.company_name = company_name
        self.year, self.month = year, month

    def insert_all(self):
        if not self.input_dir:
            log.critical("please define input_dir")
            return

        xlsx_dir = os.path.join(PROJECT_ROOT, self.input_dir)
        for filename in os.listdir(xlsx_dir):
            filepath = os.path.join(xlsx_dir, filename)
            log.debug(filepath)
            xl = self.read_excel(filepath)
            xl_content = xl.contents(row_start=2, end_before_last_row=1)

            try:
                self.insert_one_xlsx(xl_content)
            except Exception as e:
                log.critical("error occur: {}".format(e))
                continue

    def insert_one_xlsx(self, xl_contents):
        subject_lv1 = "未定义科目"
        for row in xl_contents:
            log.debug(row)
            code = row[self.code_col].strip()
            subject = row[self.subject_col].strip()
            if len(code) == 4:
                log.debug("{} is subject_lv1".format(subject))
                subject_lv1 = subject
                subject_lv2 = None
                subject_lv3 = None
            elif len(code) == 7:
                log.debug("{} is subject_lv2".format(subject))
                subject_lv2 = subject
            elif len(code) == 10:
                log.debug("{} is subject_lv3".format(subject))
                subject_lv3 = subject
            else:
                raise ValueError

            AccountBalance.create(company_name=self.company_name, is_openning_balance=True,
                                  date=datetime(year=self.year, month=self.month, day=25),
                                  subject_lv1=subject_lv1, subject_lv2=subject_lv2, subject_lv3=subject_lv3,
                                  cur_balance_debit=row[self.cur_balance_debit],
                                  cur_balance_credit=row[self.cur_balance_credit])

        return


    def read_excel(self, filepath):
        return Xlsx(filepath)


class AcctidApi():
    """科目代码"""
    input_dir = "input/acctid"
    acctid_col = 0
    acct_name_col = 1
    acct_type_col = 3
    balance_direction_col = 5
    def __init__(self, company_name):
        self.company_name = company_name

    def insert_all(self, increment=True):
        if not self.input_dir:
            log.critical("please define input_dir")
            return
        xlsx_dir = os.path.join(PROJECT_ROOT, self.input_dir)
        # 是否先清空当前公司所有科目代码？
        if not increment:
            self.remove_documents_of_company()

        for filename in os.listdir(xlsx_dir):
            filepath = os.path.join(xlsx_dir, filename)
            log.debug(filepath)
            xl = self.read_excel(filepath)
            xl_content = xl.contents(row_start=2)

            try:
                self.insert_one_xlsx(xl_content)
            except Exception as e:
                log.critical("error occur: {}".format(e))
                continue

    def insert_one_xlsx(self, xl_contents):

        for row in xl_contents:
            log.debug(row)
            acctid = str(row[self.acctid_col]).strip()
            acct_name = row[self.acct_name_col].strip()
            acct_type = row[self.acct_type_col].strip()
            balance_direction = row[self.balance_direction_col].strip()

            if not self.acctid_exists(acctid):
                Acctid.create(company_name=self.company_name, acctid=acctid, acct_name=acct_name,
                              acct_type=acct_type, balance_direction=balance_direction)

        return

    def acctid_exists(self, acctid):
        query = Acctid.select().where(
            (Acctid.company_name == self.company_name) &
            (Acctid.acctid == acctid)
        )
        if query.exists():
            log.debug(f'Acctid {acctid} exist.')
        else:
            log.debug(f'New Acctid {acctid}')

        return query.exists()

    def read_excel(self, filepath):
        return Xlsx(filepath)

    def remove_documents_of_company(self):
        Acctid.delete().where(Acctid.company_name == self.company_name).execute()
        log.info("delete accids of {}".format(self.company_name))
        return


def aggregate_data(table, pipeline):
    return list(table.objects.aggregate(*pipeline))

def delete_docs(table, filter):
    return table.delete().where(**filter)

def find_acctid(acct_name, company_name):
    """获取科目代码"""
    if not isinstance(acct_name, list):
        assert TypeError, "Input acct is not list"
    elif acct_name == [''] * 8:
        log.debug('skip! attc is empty')
        return

    res = Acctid.select().where(
        (Acctid.company_name == company_name) &
        (Acctid.acct_name == acct_name)
    )
    res = list(res)

    if not res:
        raise ValueError(f"acctid is {res}, Can not find acctid by acct_name : {acct_name}")
    assert len(res) <= 2, f"found more than 1 acctid: {res}"

    return res[0].acctid


if __name__ == '__main__':
    # bsa = BankStatementApi(company="广州南方化玻医疗器械有限公司")
    # bsa.insert_all()
    # isa = InvoiceSaleApi("广州南方化玻医疗器械有限公司")
    # isa.insert_all()
    # iba = InvoiceBuyApi("广州南方化玻医疗器械有限公司")
    # iba.insert_all()
    aa = AcctidApi(company_name="广州南方化玻医疗器械有限公司")
    aa.insert_all()
    # aa.acctid_not_exists(1231002)


