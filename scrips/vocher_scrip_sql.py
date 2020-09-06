import os, re
import datetime
from dateutil.relativedelta import relativedelta
from pprint import pprint
from playhouse.shortcuts import model_to_dict

from voucher import *
from utils import *
from utils.mongoapi import aggregate_data

log = get_logger(__name__, level=10)

# 定义凭证编号（全局常量）
num_in, num_out, num_tran = 1, 1, 1         # 收、付、转

def vocher_sale_insert(company_name, year, month):
    """从数据库销项发票，生成销项凭证，并存入数据库"""
    begin_date = datetime.date(year=year, month=month, day=1)
    end_date = begin_date + relativedelta(months=+1, seconds=-1)
    global num_tran

    object_names = Invoice.select().where(
        (Invoice.company_name == company_name) &
        (Invoice.invoice_type == "sale") &
        (Invoice.billing_date.between(begin_date, end_date))
    ).group_by(Invoice.object_name)

    # 如果有可插入的凭证，则清除已存在的同时期所有凭证，重新插入凭证。否则中止插入。
    if object_names:
        delete_vouchers_of_range(
            begin_date, end_date,
            ((Voucher.company_name == company_name) &
             (Voucher.category == "销项发票凭证"))
        )
    else:
        log.critical("Aborted! Query sale voucher and object_names not found")
        return

    for v_num, obj in enumerate(object_names):
        log.debug(f"开始构建{obj.object_name}的销项凭证")      # 获取本月所有购方企业名称

        vis = VoucherInvoiceSale(company_name, obj.object_name, year, month)
        vis.vocher_num(number=num_tran)
        vis.build_vocher()
        num_tran = num_tran + 1
    return

def vocher_buy_insert(company_name, year, month):
    """从数据库进项发票，生成进项凭证，并存入数据库"""
    begin_date = datetime.date(year=year, month=month, day=1)
    end_date = begin_date + relativedelta(months=+1, seconds=-1)
    global num_tran

    object_names = Invoice.select().where(
        (Invoice.company_name == company_name) &
        (Invoice.invoice_type == "buy") &
        (Invoice.billing_date.between(begin_date, end_date))
    ).group_by(Invoice.object_name)
    # 如果有可插入的凭证，则清除已存在的同时期所有凭证，重新插入凭证。否则中止插入。
    if object_names:
        delete_vouchers_of_range(begin_date, end_date,
                                 ((Voucher.company_name == company_name) &
                                  (Voucher.category == "进项发票凭证")))
    else:
        log.critical("Aborted! Query buy voucher and object_names not found")
        return

    for v_num, obj in enumerate(object_names):
        log.debug(f"开始构建{obj.object_name}的进项凭证")      # 获取本月所有购方企业名称

        vib = VoucherInvoiceBuy(company_name, obj.object_name, year, month)
        vib.vocher_num(number=num_tran)
        vib.build_vocher()
        num_tran = num_tran + 1
    return

def vocher_bankstatement_insert(company_name, year, month):
    """从数据库银行对账单，生成银行凭证，并存入数据库"""
    begin_date = datetime.date(year=year, month=month, day=1)
    end_date = begin_date + relativedelta(months=+1, seconds=-1)
    global num_in, num_out

    object_names = BankStatement.select().where(
        (BankStatement.company_name == company_name) &
        (BankStatement.operation_time.between(begin_date, end_date))
    ).group_by(BankStatement.object_name)

    # 如果有可插入的凭证，则清除已存在的同时期所有凭证，重新插入凭证。否则中止插入。
    if object_names:
        delete_vouchers_of_range(begin_date, end_date,
                                 ((Voucher.company_name == company_name) &
                                  (Voucher.category.contains("银行凭证"))))
    else:
        log.critical("Aborted! Query sale voucher, found: {}".format(object_names))
        return

    for v_num, obj in enumerate(object_names):
        log.debug(f"开始构建{obj.object_name}的银行对账单凭证")  # 获取本月所有购方企业名称
        vbs = VoucherBankstatement(company_name, obj.object_name, year, month, num_in, num_out)
        # vbs.voucher_exist_in_current_period()
        vbs.build_voucher_sql()
        # num_in, num_out = vbs.num_in, vbs.num_out
    return


def delete_vouchers_of_range(begin_date, end_date, other_param=()):
    # 删除凭证行
    vouchers = Voucher.select().where(
        Voucher.date.between(begin_date, end_date) &
        other_param
    )
    for voucher in vouchers:
        v = model_to_dict(voucher)
        for i in range(1, 10):
            row = v.get(f'row_{i}')
            if row:
                VoucherRow.delete_by_id(row.get("id"))
    # 删除凭证本体
    q = Voucher.delete().where(
        Voucher.date.between(begin_date, end_date) &
        other_param
    )
    delete_cnt = q.execute()

    log.info(f"delete {delete_cnt} vouchers from {begin_date} to {end_date}")
    return

if __name__ == '__main__':
    input_param = {
         "company_name": '广州南方化玻医疗器械有限公司',
         "year": 2020, "month": 8
    }
    vocher_sale_insert(**input_param)
    vocher_buy_insert(**input_param)
    vocher_bankstatement_insert(**input_param)
    # build_voucher_excel('广州南方化玻医疗器械有限公司', 2020, 1, 1, 2020, 1, 31)