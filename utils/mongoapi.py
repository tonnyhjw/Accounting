import os
from xlrd.xldate import xldate_as_datetime
from datetime import datetime

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
        self.bank_infos = Bank.objects()
        self.project_root = PROJECT_ROOT

    def insert_all(self):
        for bank_info in self.bank_infos:
            bank_xlsx_dir = os.path.join(self.project_root, bank_info.xlsx_dir)
            for filename in os.listdir(bank_xlsx_dir):
                filepath = os.path.join(bank_xlsx_dir, filename)
                log.debug(filepath)
                xl = Xlsx(filepath)
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
            outcome = 0 if not row[bank_info.outcome_col] else row[bank_info.outcome_col]
            income = 0 if not row[bank_info.income_col] else row[bank_info.income_col]
            operation_time = self.time_fmt(row[bank_info.operation_time_col])

            log.debug("outcome: {}  income:{}  operation_time: {}  org_operation_time: {}".format(outcome, income, operation_time, row[bank_info.operation_time_col]))

            BankStatement(company_name=self.company, object_account=row[bank_info.object_account_col], object_name=row[bank_info.object_name_col],
                          outcome=outcome, income=income, balance=row[bank_info.balance_col],
                          abstract=row[bank_info.abstract_col], bank=bank_info.bankname, insert_time=datetime.now(), operation_time=operation_time).save()
        return

    @staticmethod
    def time_fmt(input_time):
        if isinstance(input_time, float):
            return xldate_as_datetime(input_time, 0)
        elif isinstance(input_time, str):
            return datetime.strptime(input_time, "%Y%m%d %H:%M:%S")


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

            Invoice(company_name=self.company_name, invoice_code=previous_row[self.invoice_code], invoice_num=previous_row[self.invoice_num],
                    object_name=previous_row[self.object_name], object_tax_num=previous_row[self.object_tax_num],
                    bank_account=previous_row[self.bank_account], billing_date=billing_date, merchandise_name=previous_row[self.merchandise_name],
                    merchandise_amount=merchandise_amount, unit_price=unit_price,
                    sum_price=sum_price, tax_rate=tax/sum_price, tax=tax,
                    tax_category_code=previous_row[self.tax_category_code], invoice_type=self.invoice_type).save()
        return

class InvoiceBuyApi(InvoiceBaseApi):
    invoice_code = 1  # 发票代码
    invoice_num = 2  # 发票号码
    object_name = 5  # 销方企业名称
    object_tax_num = 4  # 购方税号
    billing_date = 3  # 开票日期
    select_date = 9   # 勾选日期
    belong_date = (1, 7)
    sum_price = 6  # 金额
    # tax_rate = 15  # 税率
    tax = 7  # 税额
    # tax_category_code = 17  # 税收分类编码
    input_dir = "input/invoice/buy"
    invoice_type = "buy"
    row_start = 4
    end_before_last_row = 0

    def insert_one_xlsx(self, xl_contents):

        belong_date = datetime.strptime(self.xls.sheet_r.row_values(self.belong_date[0])[self.belong_date[1]]+"30", "%Y%m%d")
        log.debug("belong date: {}".format(belong_date))
        for row in xl_contents:
            log.debug("row :{}".format(row))

            billing_date = self.time_fmt(row[self.billing_date])
            select_date = self.time_fmt(row[self.select_date])
            sum_price = float(row[self.sum_price]) if row[self.sum_price] else 0
            tax = float(row[self.tax]) if row[self.tax] else 0

            Invoice(company_name=self.company_name, invoice_code=row[self.invoice_code], invoice_num=row[self.invoice_num],
                    object_name=row[self.object_name], object_tax_num=row[self.object_tax_num], billing_date=billing_date,
                    sum_price=sum_price, tax_rate=tax/sum_price, tax=tax, invoice_type=self.invoice_type,
                    belong_date=belong_date, select_date=select_date).save()
        return

    def read_excel(self, filepath):
        self.xls = Xls(filepath)
        return self.xls

def aggregate_data(table, pipeline):
    return list(table.objects.aggregate(*pipeline))


if __name__ == '__main__':
    # bsa = BankStatementApi(company="广州南方化玻医疗器械有限公司")
    # bsa.insert_all()
    # isa = InvoiceSaleApi("广州南方化玻医疗器械有限公司")
    # isa.insert_all()
    iba = InvoiceBuyApi("广州南方化玻医疗器械有限公司")
    iba.insert_all()
