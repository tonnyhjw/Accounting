from utils import *
from utils.mongoapi import InitialOpenningBalanceApi

log = get_logger(__name__, level=10)

def insert_all(company_name=None):
    if not company_name:
        log.critical("Please insert company name")
    ioba = InitialOpenningBalanceApi(company_name)
    ioba.insert_all()

if __name__ == '__main__':
    insert_all("广州南方化玻医疗器械有限公司")