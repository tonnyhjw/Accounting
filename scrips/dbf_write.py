# coding:utf-8
import os
from pprint import pprint
from datetime import datetime
import dbf

from utils import *
log = get_logger(__name__, level=10)

def write_1(model_sub_dir="xlsx_model/凭证-output.dbf"):
    model_org_dir = os.path.join(PROJECT_ROOT, "xlsx_model/凭证.dbf")
    model_dir = os.path.join(PROJECT_ROOT, model_sub_dir)


    table_org = dbf.Table(model_org_dir, codepage=0x4D)
    table_out = dbf.Table(model_dir, codepage=0x4D)
    table_org.open(mode=dbf.READ_WRITE)
    table_out.open(mode=dbf.READ_WRITE)

    # for rec in table_org:
    #     new_record = {}
    #
    #     if rec["fnum"] >3:
    #         break
    #
    #     for field_name in table_org.field_names:
    #         new_record.update({field_name: rec[field_name]})
    #     pprint(new_record)
    #     table_out.append(new_record)

    # 清空所有record
    for rec in table_org:
        dbf.delete(rec)

    table_org.close()
    table_out.close()

    # record_add = {"FDATE": datetime(year=2019, month=12, day=31),
    #               "FPERIOD": 12.,
    #               "FNUM": 7.,
    #               "FENTRYID": 0,
    #               "FEXP": "结转本年利润"
    #               }
    # table.append(record_add)
    # for name in table.field_names:
    #     print(table.field_info(name))



    # for rec in records:
    #     print(rec)
    #     # dictionary = rec.as_dict()
    #     # if dictionary[b'FENTRYID'] >2:
    #     #     break
    #     # rec_1 = dbf.new_record()
    #     # for k, v in dictionary.items():
    #     #     rec_1[k] = v
    #     #     rec_1[b'FNUM'] = 7.
    #     #     rec_1[b'FEXP'] = "测试科目"
    #     #     rec_1[b'FSERIALNO'] = 22.
    #     #     dbf.write_record(rec_1)
    #
    #     print("*"*30)



    # table.close()

    return

if __name__ == '__main__':
    # write()
    write_1()