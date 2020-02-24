import datetime
from dateutil.relativedelta import relativedelta

from utils import *
from utils import mongoapi

log = get_logger(__name__, level=10)

"""银行对账单、进项发票、销项发票存入数据库"""

def all_excel_insert_db(company_name):
    bsa = mongoapi.BankStatementApi(company=company_name)
    bsa.insert_all()
    isa = mongoapi.InvoiceSaleApi(company_name)
    isa.insert_all()
    iba = mongoapi.InvoiceBuyApi(company_name)
    iba.insert_all()
    return

def delete_bank_and_invoice(company_name, year, month):
    begin_date = datetime.date(year=year, month=month, day=1)
    end_date = begin_date + relativedelta(months=+1, minutes=-1)
    DELETE_BANKSTATEMENT_FILTER = {
        "operation_time__gte": begin_date,
        "operation_time__lte": end_date,
        "company_name": company_name
    }
    DELETE_INVOICESALE_FILTER = {
        "billing_date__gte": begin_date,
        "billing_date__lte": end_date,
        "company_name": company_name,
        "invoice_type": "sale"
    }
    DELETE_INVOICEBUY_FILTER = {
        "belong_date__gte": begin_date,
        "belong_date__lte": end_date,
        "company_name": company_name,
        "invoice_type": "buy"
    }
    delete_docs(BankStatement, DELETE_BANKSTATEMENT_FILTER)
    delete_docs(Invoice, DELETE_INVOICESALE_FILTER)
    delete_docs(Invoice, DELETE_INVOICEBUY_FILTER)

    return





if __name__ == '__main__':
    all_excel_insert_db("广州南方化玻医疗器械有限公司")
    # delete_bank_and_invoice("广州南方化玻医疗器械有限公司", 2019, 12)