import os, re
from datetime import datetime
from pprint import pprint


from voucher import *
from utils import *
from utils.mongoapi import aggregate_data

log = get_logger(__name__, level=10)

# 定义凭证编号（全局常量）
num_in, num_out, num_tran = 1, 1, 1         # 收、付、转

def vocher_sale_insert(company_name, begin_y, begin_m, begin_d, end_y, end_m, end_d):
    """从数据库销项发票，生成销项凭证，并存入数据库"""
    begin_date, end_date = datetime(begin_y, begin_m, begin_d), datetime(end_y, end_m, end_d, hour=23, minute=59, second=59)
    global num_tran
    pipeline = []
    match = {"$match": {"company_name": company_name, "invoice_type": "sale",
                        "billing_date": {"$gte": begin_date, "$lte": end_date}}}
    group = {"$group": {"_id": "$object_name"}}
    pipeline.append(match)
    pipeline.append(group)
    # pprint(pipeline)

    object_names = aggregate_data(Invoice, pipeline)
    # 如果有可插入的凭证，则清除已存在的同时期所有凭证，重新插入凭证。否则中止插入。
    if object_names:
        delete_vouchers_of_range(begin_date, end_date, {"company_name": company_name, "category": "销项发票凭证"})
    else:
        log.critical("Aborted! Query sale voucher, found: {}".format(object_names))
        return

    for v_num, object_name in enumerate(object_names):
        log.debug("开始构建{}的销项凭证".format(object_name["_id"]))      # 获取本月所有购方企业名称

        vis = VoucherInvoiceSale(company_name, object_name["_id"], begin_y, begin_m, begin_d, end_y, end_m, end_d)
        vis.vocher_num(number=num_tran)
        vis.build_vocher()
        num_tran = num_tran + 1
    return

def vocher_buy_insert(company_name, begin_y, begin_m, begin_d, end_y, end_m, end_d):
    """从数据库进项发票，生成进项凭证，并存入数据库"""
    begin_date, end_date = datetime(begin_y, begin_m, begin_d), datetime(end_y, end_m, end_d)
    global num_tran
    pipeline = []
    match = {"$match": {"company_name": company_name, "invoice_type": "buy",
                        "belong_date": {"$gte": begin_date, "$lte": end_date}}}
    group = {"$group": {"_id": "$object_name"}}
    pipeline.append(match)
    pipeline.append(group)
    # pprint(pipeline)

    object_names = aggregate_data(Invoice, pipeline)
    # 如果有可插入的凭证，则清除已存在的同时期所有凭证，重新插入凭证。否则中止插入。
    if object_names:
        delete_vouchers_of_range(begin_date, end_date, {"company_name": company_name, "category": "进项发票凭证"})
    else:
        log.critical("Aborted! Query sale voucher, found: {}".format(object_names))
        return

    for v_num, object_name in enumerate(object_names):
        log.debug("开始构建{}的进项凭证".format(object_name["_id"]))      # 获取本月所有购方企业名称

        vib = VoucherInvoiceBuy(company_name, object_name["_id"], begin_y, begin_m, begin_d, end_y, end_m, end_d)
        vib.vocher_num(number=num_tran)
        vib.build_vocher()
        num_tran = num_tran + 1
    return

def vocher_bankstatement_insert(company_name, begin_y, begin_m, begin_d, end_y, end_m, end_d):
    """从数据库银行对账单，生成银行凭证，并存入数据库"""
    begin_date, end_date = datetime(begin_y, begin_m, begin_d), datetime(end_y, end_m, end_d, hour=23, minute=59,second=59)
    global num_in, num_out
    match = {"$match": {"company_name": company_name,
                        "operation_time": {"$gte": begin_date, "$lt": end_date}}}

    # pipeline_abstract = [match, {"$group": {"_id": "$abstract"}}]
    # abstracts = aggregate_data(BankStatement, pipeline_abstract)
    # for abstract in abstracts:
    #     log.debug("abstract:{}".format(abstract))

    pipeline_object_name = [match, {"$group": {"_id": "$object_name"}}]
    object_names = aggregate_data(BankStatement, pipeline_object_name)
    # 如果有可插入的凭证，则清除已存在的同时期所有凭证，重新插入凭证。否则中止插入。
    if object_names:
        delete_vouchers_of_range(begin_date, end_date, {"company_name": company_name, "category": re.compile("银行凭证.*")})
    else:
        log.critical("Aborted! Query sale voucher, found: {}".format(object_names))
        return

    for v_num, object_name in enumerate(object_names):
        vbs = VoucherBankstatement(company_name, object_name["_id"], begin_y, begin_m, begin_d, end_y, end_m, end_d, num_in, num_out)
        vbs.build_vocher()
        num_in, num_out = vbs.num_in, vbs.num_out
    return

def build_voucher_excel(company_name, begin_y, begin_m, begin_d, end_y, end_m, end_d,
                        model_sub_dir="xlsx_model/记账凭证模板.xlsx"):
    """从数据库导出所有目标公司的凭证excel"""
    begin_date, end_date = datetime(begin_y, begin_m, begin_d), datetime(end_y, end_m, end_d, hour=23, minute=59,second=59)
    match = {"$match": {"company_name": company_name,
                        "date": {"$gte": begin_date, "$lte": end_date}}}
    pipeline_object_name = [match]
    vouchers_matched = aggregate_data(Voucher, pipeline_object_name)

    model_dir = os.path.join(PROJECT_ROOT, model_sub_dir)
    output_dir = os.path.join(PROJECT_ROOT, "output", company_name)
    log.debug(model_dir)

    for voucher in vouchers_matched:
        output_filename = "{}-{}-{}-{}".format(voucher.get("method"),
                                               voucher.get("number"),
                                               voucher.get('category', '未定义凭证类型')[0],
                                               voucher.get('specific', '未定义公司名'))
        log.debug("start writing voucher excel <{}>".format(output_filename))
        # 建立excel
        model = Xlsx(model_dir, output_path="{}/{}.xlsx".format(output_dir, output_filename))

        # 写入公司名
        model.write_cell(1, 5, voucher.get("company_name"))
        # 写入凭证日期
        model.write_cell(3, 4,  "{} 年 {} 月 {} 日".format(voucher.get("date").year, voucher.get("date").month, voucher.get("date").day))
        # 写入具体表格内容
        model.write_row(row_index=6, row_contents=voucher.get("row_1"))
        model.write_row(row_index=7, row_contents=voucher.get("row_2"))
        model.write_row(row_index=8, row_contents=voucher.get("row_3"))
        model.write_row(row_index=9, row_contents=voucher.get("row_4"))
        model.write_row(row_index=10, row_contents=voucher.get("row_5"))
        model.write_row(row_index=11, row_contents=voucher.get("row_6"))

        # 写入凭证编号
        model.write_cell(3, 8, voucher.get("number", ""))
        # 写入收付转
        model.write_cell(3, 7, voucher.get("method", ""))

        try:
            model.output()
        except FileNotFoundError:
            os.mkdir(output_dir)
            model.output()

        log.debug("finished writing excel.")

    return

def delete_vouchers_of_range(begin_date, end_date, other_param={}):
    date_filter = {
        "date__gte": begin_date,
        "date__lte": end_date,
    }
    delete_filter = {**date_filter, **other_param}
    delete_docs(Voucher, delete_filter)

    log.info("delete documents from {} to {}".format(begin_date, end_date))
    return

if __name__ == '__main__':
    input_param = {
         "company_name": '广州南方化玻医疗器械有限公司',
         "begin_y": 2020, "begin_m": 7, "begin_d": 1,
         "end_y": 2020, "end_m": 7, "end_d": 31
    }
    vocher_sale_insert(**input_param)
    vocher_buy_insert(**input_param)
    vocher_bankstatement_insert(**input_param)
    # build_voucher_excel('广州南方化玻医疗器械有限公司', 2020, 1, 1, 2020, 1, 31)