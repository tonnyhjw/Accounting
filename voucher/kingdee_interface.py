"""
对接坑爹凭证
"""

import os
import shutil
import dbf
import datetime

from utils import *

class KingdeeInterface(object):
    DBF_MODEL = os.path.join(PROJECT_ROOT, "xlsx_model/凭证.dbf")
    DBF_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
    records = []

    def __init__(self, company_name, year, month, customise_output_name=True):
        self.company_name = company_name
        self.year, self.month = year, month
        if customise_output_name:
            self.DBF_OUTPUT_FILE = os.path.join(self.DBF_OUTPUT_DIR, "{}{}年{}月.dbf".format(self.company_name, self.year, self.month))
        self._copy_dbf_model()


    def _copy_dbf_model(self):
        """复制模板用作输出"""
        shutil.copy2(src=self.DBF_MODEL, dst=self.DBF_OUTPUT_FILE)

    def load_records(self):
        return

    def write_dbf(self):
        table_out = dbf.Table(self.DBF_OUTPUT_FILE, codepage=0x4D)
        table_out.open(dbf.READ_WRITE)
        for record in self.records:
            table_out.append(record)
        table_out.close()
        return

if __name__ == '__main__':
    ki = KingdeeInterface('广州南方化玻医疗器械有限公司', 2019, 12)
