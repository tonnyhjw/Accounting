from pprint import pprint
from datetime import datetime

from voucher import *
from utils.helpers import get_logger
from utils.models import Invoice, BankStatement
from utils.mongoapi import aggregate_data

log = get_logger(__name__, level=10)

def vocher_scrip_sale(company_name, begin_y, begin_m, begin_d, end_y, end_m, end_d):
    begin_date, end_date = datetime(begin_y, begin_m, begin_d), datetime(end_y, end_m, end_d)
    pipeline = []
    match = {"$match": {"company_name": company_name, "invoice_type": "sale",
                        "billing_date": {"$gte": begin_date, "$lt": end_date}}}
    group = {"$group": {"_id": "$object_name"}}
    pipeline.append(match)
    pipeline.append(group)
    # pprint(pipeline)

    object_names = aggregate_data(Invoice, pipeline)
    for v_num, object_name in enumerate(object_names):
        log.debug("开始构建{}的销项凭证".format(object_name["_id"]))      # 获取本月所有购方企业名称

        vis = VoucherInvoiceSale(company_name, object_name["_id"], begin_y, begin_m, begin_d, end_y, end_m, end_d)
        vis.vocher_num(number=v_num+1)
        vis.build_vocher()

    return

def vocher_scrip_buy(company_name, begin_y, begin_m, begin_d, end_y, end_m, end_d):
    begin_date, end_date = datetime(begin_y, begin_m, begin_d), datetime(end_y, end_m, end_d)
    pipeline = []
    match = {"$match": {"company_name": company_name, "invoice_type": "buy",
                        "belong_date": {"$gte": begin_date, "$lt": end_date}}}
    group = {"$group": {"_id": "$object_name"}}
    pipeline.append(match)
    pipeline.append(group)
    # pprint(pipeline)

    object_names = aggregate_data(Invoice, pipeline)
    for v_num, object_name in enumerate(object_names):
        log.debug("开始构建{}的进项凭证".format(object_name["_id"]))      # 获取本月所有购方企业名称

        vis = VoucherInvoiceBuy(company_name, object_name["_id"], begin_y, begin_m, begin_d, end_y, end_m, end_d)
        vis.vocher_num(number=v_num + 1)
        vis.build_vocher()

    return

def vocher_scrip_bankstatement(company_name, begin_y, begin_m, begin_d, end_y, end_m, end_d):
    begin_date, end_date = datetime(begin_y, begin_m, begin_d), datetime(end_y, end_m, end_d)
    match = {"$match": {"company_name": company_name,
                        "operation_time": {"$gte": begin_date, "$lt": end_date}}}
    pipeline_abstract = [match, {"$group": {"_id": "$abstract"}}]
    pipeline_object_name = [match, {"$group": {"_id": "$object_name"}}]

    abstracts = aggregate_data(BankStatement, pipeline_abstract)
    object_names = aggregate_data(BankStatement, pipeline_object_name)
    # for abstract in abstracts:
    #     log.debug("abstract:{}".format(abstract))
    for object_name in object_names:
        vbs = VoucherInvoiceBankstatement(company_name, object_name["_id"], begin_y, begin_m, begin_d, end_y, end_m, end_d)
        vbs.build_vocher()
    return



if __name__ == '__main__':
    vocher_scrip_sale('广州南方化玻医疗器械有限公司', 2019, 11, 1, 2019, 11, 30)
    vocher_scrip_buy('广州南方化玻医疗器械有限公司', 2019, 11, 1, 2019, 11, 30)
    vocher_scrip_bankstatement('广州南方化玻医疗器械有限公司', 2019, 11, 1, 2019, 11, 30)