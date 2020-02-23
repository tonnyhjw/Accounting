import os
import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

BALANCE_SHEET_MODEL = os.path.join(PROJECT_ROOT, "xlsx_model/资产负债表.xlsx")

# 开账期初数科目分类
# 只有一级科目
SINGLE_GRADE = ['现金', '应付工资', '实收资本', '本年利润', '主营业务收入',
                '营业外收入', '主营业务成本', '所得税']
# 有一级科目和二级科目
DOUBLE_GRADE = ['银行存款', '应收账款', '预付账款', '其他应收款', '库存商品',
                '固定资产', '累计折旧', '应付账款', '其他应付款',
                '盈余公积', '利润分配', '主营业务税金及附加', '营业费用', '管理费用', '财务费用']

TRIPLE_GRADE = ['应交税费']

DEFUALT_KD_RECORD = {
    'facctid': '1002                                                                                                                                                                                                                                                          ',
    'fattchment': None,
    'fcash': '        ',
    'fcashflow': None,
    'fchecker': '梁卉琳              ',
    'fclsname1': '                    ',
    'fclsname2': '                    ',
    'fclsname3': '                    ',
    'fclsname4': '                    ',
    'fcredit': 0.0,
    'fcyid': 'RMB',
    'fdate': datetime.date(2019, 12, 31),
    'fdc': 'D',
    'fdebit': 0.0,
    'fdeleted': False,
    'fentryid': 0.0,
    'fexchrate': 1.0,
    'fexp': '交电话费（12月）                                            ',
    'ffcyamt': 0.0,
    'fgroup': '记  ',
    'fmodule': '    ',
    'fnum': 3.0,
    'fobjid1': '                    ',
    'fobjid2': '                    ',
    'fobjid3': '                    ',
    'fobjid4': '                    ',
    'fobjname1': '                                        ',
    'fobjname2': '                                        ',
    'fobjname3': '                                        ',
    'fobjname4': '                                        ',
    'fpay': '        ',
    'fperiod': 12.0,
    'fposted': False,
    'fposter': 'Manager             ',
    'fprepare': 'Manager             ',
    'fprice': 0.0,
    'fqty': 0.0,
    'freference': '                                                  ',
    'fserialno': 18.0,
    'fsettlcode': '        ',
    'fsettleno': '          ',
    'ftransdate': None,
    'ftransid': '                    ',
    'funitname': '                                                  '
}
