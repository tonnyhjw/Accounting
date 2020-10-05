import os
import datetime
from dateutil.relativedelta import relativedelta
from pprint import pprint

from voucher import *
from utils import get_logger
from utils.models import Invoice
from utils.models_sql import Invoice as InvoiceSql, VoucherRow
from utils.mongoapi import aggregate_data

"""
进项发票凭证生成
"""

log = get_logger(__name__, level=10)

class VoucherInvoiceBuy(VoucherBase):

    def __init__(self, company_name, object_name, year, month):
        super(VoucherInvoiceBuy, self).__init__()
        self.category = "进项发票凭证"
        self.company_name = company_name
        self.object_name = object_name
        self.output_dir = os.path.join(self.output_dir, self.company_name)
        self.begin_date = datetime.date(year=year, month=month, day=1)
        self.end_date = self.begin_date + relativedelta(months=+1, seconds=-1)
        self.load_model(output_filename="进项发票凭证-"+self.object_name)

    def sum_price(self):
        """填写总收入"""
        pipeline = []
        match = {"$match": {"company_name":self.company_name, "object_name":self.object_name, "invoice_type": "buy",
                            "belong_date": {"$gte": self.begin_date, "$lte": self.end_date}}}
        group = {"$group": {"_id": "$object_name", "total": {"$sum": '$sum_price'}}}
        pipeline.append(match)
        pipeline.append(group)
        # pprint(pipeline)
        sum_price_data = aggregate_data(Invoice, pipeline)
        log.critical("sum_price_data is : {}".format(sum_price_data))
        self.sum_price_of_object = sum_price_data[0]['total']
        self.model.write_cell(6, 2, "购入")
        self.model.write_cell(6, 4, "库存商品")
        self.model.write_cell(6, 6, self.sum_price_of_object)

        self.db_object["row_1"][2] = "购入"
        self.db_object["row_1"][4] = "库存商品"
        self.db_object["row_1"][6] = self.sum_price_of_object
        return self.sum_price

    def tax(self):
        """填写应交税费"""
        pipeline = []
        match = {"$match": {"company_name":self.company_name, "object_name":self.object_name, "invoice_type": "buy",
                            "belong_date": {"$gte": self.begin_date, "$lte": self.end_date}}}
        group = {"$group": {"_id": "$object_name", "total": {"$sum": '$tax'}}}
        pipeline.append(match)
        pipeline.append(group)
        # pprint(pipeline)
        self.tax_of_object = aggregate_data(Invoice, pipeline)[0]['total']
        log.debug(self.tax_of_object)
        self.model.write_cell(7, 2, "进项税额")
        self.model.write_cell(7, 4, "应交税费")
        self.model.write_cell(7, 5, "进项税额")
        self.model.write_cell(7, 6, self.tax_of_object)

        self.db_object["row_2"][2] = "进项税额"
        self.db_object["row_2"][4] = "应交税费"
        self.db_object["row_2"][5] = "进项税额"
        self.db_object["row_2"][6] = self.tax_of_object
        return self.sum_price

    def object_loan(self):
        """填写应收账款"""
        self.model.write_cell(8, 2, "应付")
        self.model.write_cell(8, 4, "应付账款")
        self.model.write_cell(8, 5, self.object_name)
        self.model.write_cell(8, 7, self.sum_price_of_object+self.tax_of_object)

        self.db_object["row_3"][2] = "应付"
        self.db_object["row_3"][4] = "应付账款"
        self.db_object["row_3"][5] = self.object_name
        self.db_object["row_3"][7] = self.sum_price_of_object+self.tax_of_object

    def sql_rows(self):
        res = InvoiceSql.select(InvoiceSql.sum_price, InvoiceSql.tax).where(
            (InvoiceSql.company_name == self.company_name) &
            (InvoiceSql.object_name == self.object_name) &
            (InvoiceSql.invoice_type == "buy") &
            (InvoiceSql.belong_date.between(self.begin_date, self.end_date))
        )
        self.sum_price_of_object = sum([i.sum_price for i in res])
        self.tax_of_object = sum([i.tax for i in res])

        log.debug(f"sum price: {self.sum_price_of_object}, sum tax: {self.tax_of_object}")

        self.db_object["row_2"] = VoucherRow.create(index_2="进项税额", index_4="应交税费",index_5="进项税额",
                                                    index_6=self.tax_of_object)
        self.db_object["row_1"] = VoucherRow.create(index_2="购入", index_4="库存商品",
                                                    index_6=self.sum_price_of_object)
        self.db_object["row_3"] = VoucherRow.create(index_2="应付", index_4="应付账款", index_5=self.object_name,
                                                    index_7=self.sum_price_of_object+self.tax_of_object)


    def build_vocher(self):
        """"""
        self.write_company_name()
        self.write_end_date()
        self.wirte_specific(self.object_name)
        self.sql_rows()
        # self.sum_price()
        # self.tax()
        # self.object_loan()
        # self.insert_db()
        # self.output()
        self.transfer_method()
        self.insert_sql()



if __name__ == '__main__':
    vs = VoucherInvoiceBuy('广州南方化玻医疗器械有限公司', "广州市侨鑫医疗器械科技发展有限公司", 2019, 10, 1, 2019, 10, 31)
    vs.build_vocher()
