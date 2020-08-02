"""
对接坑爹凭证
"""

import os
import shutil
import dbf
import copy
import datetime
from pprint import pprint

from utils import *
from utils.mongoapi import aggregate_data, find_acctid

log = get_logger(__name__, level=10)

class KingdeeInterface(object):
    DBF_MODEL = os.path.join(PROJECT_ROOT, "xlsx_model/凭证.dbf")
    DBF_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
    records = []
    incorrect_acctname = []

    def __init__(self, company_name, year, month, customise_output_name=True):
        self.company_name = company_name
        self.year, self.month = year, month
        if customise_output_name:
            self.DBF_OUTPUT_FILE = os.path.join(self.DBF_OUTPUT_DIR, "{}{}年{}月.dbf".format(self.company_name, self.year, self.month))
        self._copy_dbf_model()


    def _copy_dbf_model(self):
        """复制模板用作输出"""
        shutil.copy2(src=self.DBF_MODEL, dst=self.DBF_OUTPUT_FILE)

    def load_vouchers(self):
        """读取所有凭证"""
        project = {
            "$project": {
                "doc": "$$ROOT",
                "year": {"$year": "$date"},
                "month": {"$month": "$date"},
                "day": {"$dayOfMonth": "$date"},
                "company_name": 1
            }
        }
        match = {"$match": {"company_name": self.company_name,
                            "month": self.month, "year": self.year}}

        pipeline = [project, match]
        self.vouchers = aggregate_data(Voucher, pipeline)

        return

    def vouchers2records(self):
        for voucher in self.vouchers:
            # log.debug(voucher)
            self.build_records(voucher["doc"])

        return


    def build_records(self, voucher):
        """处理凭证种所有科目"""
        # pprint(voucher)
        log.debug("building records of voucher {}-{} {}".format(voucher.get('method'), voucher.get('number'), voucher.get('category')))
        for i in range(9):
            log.info("i:{} row:{}".format(i,voucher['row_{}'.format(1+i)]))
            self.build_one_racord(voucher['row_{}'.format(1+i)], voucher['company_name'], voucher["date"], voucher["number"], i, voucher["method"])
        # self.build_one_racord(voucher['row_2'], voucher['company_name'], voucher["date"], voucher["number"], 1., voucher["method"])
        # self.build_one_racord(voucher['row_3'], voucher['company_name'], voucher["date"], voucher["number"], 2., voucher["method"])
        # self.build_one_racord(voucher['row_4'], voucher['company_name'], voucher["date"], voucher["number"], 3., voucher["method"])
        # self.build_one_racord(voucher['row_5'], voucher['company_name'], voucher["date"], voucher["number"], 4., voucher["method"])
        # self.build_one_racord(voucher['row_6'], voucher['company_name'], voucher["date"], voucher["number"], 5., voucher["method"])

        return

    def write_dbf(self):
        table_out = dbf.Table(self.DBF_OUTPUT_FILE, codepage=0x4D)
        table_out.open(dbf.READ_WRITE)
        for record in self.records:
            table_out.append(record)
        table_out.close()
        return

    def build_one_racord(self, row, company_name, date, fnum, fentryid, fgroup):
        """根据每张凭证每行生成record"""
        lv1_idx, lv2_idx, acct_name = 4, 5, None
        if row == [""]*8:
            # 若row为8个空字符，则跳过
            log.debug("This row is empty. Skip")
            return
        elif row[lv2_idx]:
            # 若row存在二级科目，则按二级科目选择科目代码
            log.debug("exist lv2 acct {}".format(row[lv2_idx]))
            acct_name = row[lv2_idx]
        elif row[lv1_idx] and not row[lv2_idx]:
            # 若row不存在二级科目，且存在一级科目，则按一级科目查询科目代码
            log.debug("lv2 acct not exist, lv1 acct is {}".format(row[lv2_idx]))
            acct_name = row[lv1_idx]
        else:
            # 其余情况报错
            log.debug("raise ioerror")
            # raise IOError("acct input missing, row: {}".format(row))

        try:
            acctid = find_acctid(acct_name, company_name)
        except ValueError:
            log.info("Encounter ValueError when finding acctid of {}, try to handle special char".format(acct_name))
            acct_name = self.special_char_handler(acct_name)
            log.info("new acct_name :{}".format(acct_name))
            acctid = find_acctid(acct_name, company_name)
        except Exception as e:
            # 正式版需注释本段，让报错中止程序
            log.info("miss acctid {}".format(acct_name))
            log.critical("\nerr message:{}".format(e))
            self.incorrect_acctname.append(acct_name)
            return

        log.debug("acctid is {}".format(acctid))
        new_record = copy.deepcopy(DEFUALT_KD_RECORD)
        new_record["facctid"] = acctid                                  # 科目代码
        new_record["fdate"] = date                                      # 日期
        new_record["fperiod"] = float(date.month)                       # 会计周期
        new_record["fnum"] = fnum                                       # 凭证号
        new_record["fentryid"] = fentryid                               # 行数
        new_record["fgroup"] = fgroup                                   # 收付转
        new_record["fexp"] = row[2]                                     # 摘要

        # 写入借贷
        assert row[6] != '' or row[7] != '', "Row missing credit debit! row:{}".format(row)
        if row[6] != '' and not row[7]:
            new_record["fdebit"] = row[6]
            new_record["fdc"] = "D"
            new_record["ffcyamt"] = row[6]
        elif row[7] != '' and not row[6]:
            new_record["fcredit"] = row[7]
            new_record["fdc"] = "C"
            new_record["ffcyamt"] = row[7]

        self.records.append(new_record)
        return

    @staticmethod
    def special_char_handler(input_str):
        if "(" in input_str or ")" in input_str:
            # 若有英文括号存在，则换成中文括号
            input_str = input_str.replace("(", "（").replace(")", "）")
        elif "（" in input_str or "）" in input_str:
            # 若有中文括号存在，则换成英文括号
            input_str = input_str.replace("（", "(").replace("）", ")")

        return input_str

    def fail_records(self):
        log.critical("record fails")
        pprint(self.incorrect_acctname)

if __name__ == '__main__':
    ki = KingdeeInterface('广州南方化玻医疗器械有限公司', 2020, 6)
    ki.load_vouchers()
    ki.vouchers2records()
    ki.write_dbf()
    ki.fail_records()
