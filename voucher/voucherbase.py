import os
from datetime import datetime
from playhouse.shortcuts import model_to_dict

from utils import *

log = get_logger(__name__, level=10)

class VoucherBase(object):
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.model_sub_dir, object_name = None, None
        self.output_dir = os.path.join(PROJECT_ROOT, "output")
        self.company_name = "未定义企业名"
        self.category = "未定义凭证"
        self.model_sub_dir = "xlsx_model/记账凭证模板.xlsx"
        self.row_len = 1+7       # list 类型一行由0开始算，但是excel类型一行由1开始算，因此在list类型前加一行，写入excel时调用enumerate即可
        self.reset_db_object()

    def load_model(self, output_filename="测试"):
        if not self.model_sub_dir:
            log.info("model_sub_dir is not defined")
            return
        self.model_dir = os.path.join(self.project_root, self.model_sub_dir)
        self.model = Xlsx(self.model_dir, output_path="{}/{}.xlsx".format(self.output_dir, output_filename))
        return

    def iter_model(self):
        """逐行打印当前载入凭证模板"""
        for row in self.model.contents():
            log.debug(row)

    def output(self):
        try:
            self.model.output()
        except FileNotFoundError:
            os.mkdir(self.output_dir)
            self.model.output()
        return

    def vocher_num(self, number=1):
        """
        编辑凭证号
        :param number: 凭证编号
        :return:
        """
        v_num = ["收", "付", "转"]
        self.db_object["number"] = str(number)
        return

    def transfer_method(self, method=2):
        """
        右上角：收、付、转
        :param method: 0-收、1-付、2-转
        :return:
        """
        v_num = ["收", "付", "转"]
        self.db_object["method"] = v_num[method]
        log.debug("set transfer_method to {}".format(v_num[method]))
        return

    def write_company_name(self):
        self.db_object["company_name"] = self.company_name
        self.model.write_cell(1, 5, self.company_name)
        return

    def write_end_date(self):
        try:
            self.db_object["date"] = self.end_date
            self.model.write_cell(3, 4, "{} 年 {} 月 {} 日".format(self.end_date.year, self.end_date.month, self.end_date.day))
        except Exception as e:
            log.critical(e)
        return

    def insert_db(self):
        """将凭证存入MongoDB"""
        yes = {'yes', 'y', 'ye', ''}
        no = {'no', 'n'}

        self.write_category()
        log.debug("try insert voucher : {}".format(self.db_object))
        if not Voucher.objects(**self.db_object):
            log.debug("Start insert, voucher dose not exist")
            Voucher(**self.db_object).save()
        else:
            log.info("凭证已存在! 请问是否继续？ 输入y/n")
            choice = input().lower()
            assert choice not in no, "停止运行"
            if choice in yes:
                log.info("跳过该凭证")
            else:
                self.insert_db()
        return

    def insert_sql(self):
        """将凭证存入MariaDB"""
        yes = {'yes', 'y', 'ye', ''}
        no = {'no', 'n'}

        self.write_category()
        log.debug(f"try insert voucher : {self.db_object}")

        if not self.same_voucher_in_current_period().exists():
            log.debug("Start insert, voucher dose not exist")
            Voucher.create(**self.db_object)
        else:
            log.info("凭证已存在! 请问是否继续？ 输入y/n")
            choice = input().lower()
            assert choice not in no, "停止运行"
            if choice in yes:
                log.info("跳过该凭证")
            else:
                self.insert_sql()
        return

    def same_voucher_in_current_period(self):
        return Voucher.select().where(
            (Voucher.date.between(self.begin_date, self.end_date)) &
            (Voucher.company_name == self.company_name) &
            (Voucher.specific == self.object_name) &
            (Voucher.category == self.category)
        )

    def reset_db_object(self, db_type='sql'):
        """用于复位"""
        if db_type == 'sql':
            self.db_object = {}
        elif db_type == 'mongo':
            self.db_object = {
                "row_1": [""] * self.row_len,
                "row_2": [""] * self.row_len,
                "row_3": [""] * self.row_len,
                "row_4": [""] * self.row_len,
                "row_5": [""] * self.row_len,
                "row_6": [""] * self.row_len,
                "row_7": [""] * self.row_len,
                "row_8": [""] * self.row_len,
                "row_9": [""] * self.row_len,
            }

    def write_category(self):
        self.db_object["category"] = self.category
        return

    def wirte_specific(self, specific=None):
        """数据库信息增加object_name"""
        assert specific, "specific is not defined"
        self.db_object["specific"] = specific
        return