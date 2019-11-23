import os
from datetime import datetime

from utils import *

log = get_logger(__name__, level=10)

class VoucherBase():
    project_root = PROJECT_ROOT
    model_sub_dir = None
    output_dir = os.path.join(PROJECT_ROOT, "output")

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