from utils import *
from utils.mongoapi import InitialOpenningBalanceApi

log = get_logger(__name__, level=10)

def insert_all(company_name, year, month):
    ioba = InitialOpenningBalanceApi(company_name, year, month)
    ioba.insert_all()

if __name__ == '__main__':
    insert_all("广州南方化玻医疗器械有限公司", 2019, 10)