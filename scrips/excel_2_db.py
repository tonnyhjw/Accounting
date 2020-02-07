from utils import *
from utils import mongoapi

log = get_logger(__name__, level=10)

def all_excel_insert_db(company_name):
    bsa = mongoapi.BankStatementApi(company=company_name)
    bsa.insert_all()
    isa = mongoapi.InvoiceSaleApi(company_name)
    isa.insert_all()
    iba = mongoapi.InvoiceBuyApi(company_name)
    iba.insert_all()
    return

if __name__ == '__main__':
    all_excel_insert_db("广州南方化玻医疗器械有限公司")