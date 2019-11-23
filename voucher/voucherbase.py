import os
from datetime import datetime

from utils import *

log = get_logger(__name__, level=10)

class VoucherBase():
    project_root = PROJECT_ROOT
    model_sub_dir = None
    output_dir = os.path.join(PROJECT_ROOT, "output")
    company_name = "未设定企业名"


    def load_model(self, output_filename="测试"):
        if not self.model_sub_dir:
            log.info("model_sub_dir is not defined")
            return
        self.model_dir = os.path.join(self.project_root, self.model_sub_dir)
        self.model = Xlsx(self.model_dir, output_path="{}/{}.xlsx".format(self.output_dir, output_filename))
        return

    def iter_mdoel(self):
        for row in self.model.contents():
            print(row)

    def output(self):
        try:
            self.model.output()
        except FileNotFoundError:
            os.mkdir(self.output_dir)
            self.model.output()
        return

    def vocher_num(self, method=2, number=1):
        """
        编辑凭证号
        :param method: 0 = 收；1 = 付，2 = 转
        :param number:
        :return:
        """
        v_num = ["收", "付", "转"]
        self.model.write_cell(3, 7, v_num[method])
        self.model.write_cell(3, 8, str(number))
        return

    def write_company_name(self):
        self.model.write_cell(1, 5, self.company_name)
        return

    def write_end_date(self):
        try:
            self.model.write_cell(3, 5, "{} 年 {} 月 {} 日".format(self.end_y, self.end_m, self.end_d))
        except Exception as e:
            log.critical(e)
        return