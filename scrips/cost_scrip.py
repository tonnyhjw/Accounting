import datetime
from dateutil.relativedelta import relativedelta
from pprint import pprint
import random
import os

from utils import get_logger
from utils import configs
from utils import xlsx_utils
from utils.models import Invoice
from utils.mongoapi import aggregate_data

"""
成本计算
"""

log = get_logger(__name__, level=10)

def cost(company_name, year, month, range_btn=0.68, range_top=0.7):
    begin_date = datetime.datetime(year=year, month=month, day=1)
    end_date = begin_date + relativedelta(months=+1, minutes=-1)
    match = {"$match": {"company_name": company_name, "invoice_type": "sale",
                        "billing_date": {"$gte": begin_date,
                                         "$lte": end_date}}}
    group = {"$group": {"_id": "$merchandise_name",
                        "sumprice": {"$sum": '$sum_price'},
                        "amount": {"$sum": '$merchandise_amount'}}}
    # project = {"$project": {"merchandise_name":1, 'sum_price':1, "merchandise_amount":1}}
    pipeline = [match, group]

    pprint(pipeline)

    datas = aggregate_data(Invoice, pipeline)
    price, cost = 0, 0
    model_dir = os.path.join(configs.PROJECT_ROOT, "xlsx_model/成本模板.xls")
    output_dir = os.path.join(configs.PROJECT_ROOT, "output")
    model = xlsx_utils.Xls(model_dir, output_path="{}/{}.xls".format(output_dir, "cost"))


    for i, data in enumerate(datas):
        param = random.uniform(range_btn, range_top)
        # print(param)
        print(data)
        # print("{}: {} * {}".format(i, data.get('sumprice'), param))
        price += data.get('sumprice')
        cost += data.get('sumprice')*param
        model.write_cell(i + 2, 1, data.get("_id"))
        model.write_cell(i + 2, 2, data.get("amount"))
        model.write_cell(i + 2, 4, data.get('sumprice')*param)
        model.write_cell(i + 2, 5, data.get('sumprice'))
        try:
            model.write_cell(i + 2, 3, data.get('sumprice')*param / data.get("amount"))
        except ZeroDivisionError:
            print("float division by zero")
    model.write_cell(i + 3, 4, cost)
    model.write_cell(i + 3, 5, price)
    model.output()
    print("\nsum price is {}".format(price))
    print("cost is {}".format(cost))



    return

if __name__ == '__main__':
    cost('广州南方化玻医疗器械有限公司', 2020, 5, range_btn=0.77, range_top=0.82)