from pprint import pprint
from mongoengine import *

connect('accounting', username='hjw', password='newton123')

class Bank(Document):
    bankname = StringField(unique=True, required=True)
    bankcode = IntField(unique=True)
    starting_row = IntField(required=True)
    ending_row = IntField(required=True)
    content_sheet = IntField(required=True)
    operation_time_col = IntField(required=True)
    object_account_col = IntField(required=True)
    object_name_col = IntField(required=True)
    outcome_col = IntField(required=True)
    income_col = IntField(required=True)
    balance_col = IntField(required=True)
    abstract_col = IntField(required=True)
    xlsx_dir = StringField(unique=True)

    def json(self):
        bank_dict = {
            "bankname": self.bankname,
            "bankcode": self.bankcode,
            "starting_row": self.starting_row,
            "ending_row": self.ending_row,
            "content_sheet": self.content_sheet,
            "operation_time_col": self.operation_time_col,
            "object_account_col": self.object_account_col,
            "object_name_col": self.object_name_col,
            "outcome_col": self.outcome_col,
            "income_col": self.income_col,
            "balance_col": self.balance_col,
            "abstract_col": self.abstract_col,
            "xlsx_dir": self.xlsx_dir
        }
        return bank_dict

    meta = {
        "indexes": ["bankname"]
    }

class BankStatement(Document):
    company_name = StringField(required=True)       # 所属企业名
    operation_time = DateTimeField(required=True)   # 交易时间
    object_account = StringField(default="")        # 对方账号
    object_name = StringField(default="")           # 对方户名
    outcome = FloatField(default=0)                 # 支出
    income = FloatField(default=0)                  # 存入
    balance = FloatField(required=True)             # 余额
    abstract = StringField(required=True)           # 摘要
    bank = StringField(required=True)               # 所属银行
    insert_time = DateTimeField(required=True)      # 写入时间

    def json(self):
        bank_statement_dict = {
            "company_name": self.company_name,
            "operation_time": self.operation_time,
            "object_account": self.object_account,
            "object_name": self.object_name,
            "outcome": self.outcome,
            "income": self.income,
            "balance": self.balance,
            "abstract": self.abstract,
            "bank": self.bank,
            "insert_time": self.insert_time
        }
        return bank_statement_dict

    meta = {
        "indexes": ["operation_time", "object_name", "balance"],
        "ordering": ["-operation_time"]
    }


class Invoice(Document):
    company_name = StringField(required=True)           # 公司名称
    invoice_code = StringField(required=True)           # 发票代码
    invoice_num = StringField(required=True)            # 发票号码
    object_name = StringField()                         # 购方企业名称
    object_tax_num = StringField()                      # 购方税号
    bank_account = StringField()                        # 银行账号
    billing_date = DateTimeField(required=True)         # 开票日期
    merchandise_name = StringField()                    # 商品名称
    merchandise_amount = IntField()                     # 数量
    unit_price = FloatField()                           # 单价
    sum_price = FloatField(required=True)               # 金额
    tax_rate = FloatField()                             # 税率
    tax = FloatField(required=True)                     # 税额
    tax_category_code = StringField()                   # 税收分类编码
    invoice_type = StringField(required=True)           # 发票类型（销项发票、进项发票等）
    select_date = DateTimeField()                       # 勾选日期
    belong_date = DateTimeField()                       # 所属月份

    def json(self):
        invoice_dict = {
            "company_name": self.company_name,
            "invoice_code": self.invoice_code,
            "invoice_num": self.invoice_num,
            "object_name": self.object_name,
            "object_tax_num": self.object_tax_num,
            "bank_account": self.bank_account,
            "billing_date": self.billing_date,
            "merchandise_name": self.merchandise_name,
            "merchandise_amount": self.merchandise_amount,
            "unit_price": self.unit_price,
            "sum_price": self.sum_price,
            "tax_rate": self.tax_rate,
            "tax": self.tax,
            "tax_category_code": self.tax_category_code,
            "invoice_type": self.invoice_type,
            "select_date": self.select_date,
            "belong_date": self.belong_date,
        }
        return invoice_dict

    meta = {
        "indexes": ["invoice_code"]
    }

class InitialOpenningBalance(Document):
    """开账期初数"""
    company_name = StringField(required=True)                       # 公司名称
    object_name = StringField(required=True)                        # 科目名称
    debita_init_openning_balance = FloatField(required=True)        # 借方开账期初数
    fidem_init_openning_balance = FloatField(required=True)         # 贷方开账期初数
    first_grade = StringField(required=True)                        # 期初数一级科目 （应付账款、预付账款、等等）
    open_date = DateTimeField()                                     # 开账日期 （年月）

    def json(self):
        initial_openning_balance_dict = {
            "company_name": self.company_name,
            "object_name": self.object_name,
            "debita_init_openning_balance": self.debita_init_openning_balance,
            "fidem_init_openning_balance": self.fidem_init_openning_balance,
            "first_grade": self.first_grade
        }
        return initial_openning_balance_dict

    meta = {
        "indexes": ["company_name", "object_name",
                    "debita_init_openning_balance", "fidem_init_openning_balance"]
    }

class Voucher(Document):
    """凭证"""
    company_name = StringField(required=True)   # 本公司名称
    specific = StringField(required=True)       # 凭证具体所属事项（进/销目标、其他费用、现金等）
    date = DateTimeField(required=True)         # 凭证所属日期
    category = StringField(required=True)       # 凭证类型
    number = StringField()                      # 凭证号
    method = StringField()                      # 收、付、转
    supervisor = StringField()                  # 主管
    reviewer = StringField()                    # 审核
    cashier = StringField()                     # 出纳
    producer = StringField()                    # 制单
    row_1 = ListField()                         # 第一行
    row_2 = ListField()                         # 第二行
    row_3 = ListField()                         # 第三行
    row_4 = ListField()                         # 第四行
    row_5 = ListField()                         # 第五行
    row_6 = ListField()                         # 第六行
    row_7 = ListField()                         # 第七行
    row_8 = ListField()                         # 第八行
    row_9 = ListField()                         # 第九行

    def json(self):
        voucher_dict = {
            "company_name": self.company_name,
            "specific": self.specific,
            "date": self.date,
            "category": self.category,
            "number": self.number,
            "method": self.method,
            "supervisor": self.supervisor,
            "reviewer": self.reviewer,
            "cashier": self.cashier,
            "producer": self.producer,
            "row_1": self.row_1,
            "row_2": self.row_2,
            "row_3": self.row_3,
            "row_4": self.row_4,
            "row_5": self.row_5,
            "row_6": self.row_6,
            "row_7": self.row_7,
            "row_8": self.row_8,
            "row_9": self.row_9,
        }
        return voucher_dict

    meta = {
        "indexes": ["company_name", "method", "number"],
        "ordering": ["-year"]
    }

class AccountBalance(Document):
    """科目余额表"""
    company_name = StringField(required=True)           # 公司名称
    is_openning_balance = BooleanField(required=True)   # 是否开账余额
    date = DateTimeField(required=True)                 # 所属日期
    subject_lv1 = StringField(required=True)            # 一级科目
    subject_lv2 = StringField(default=None)             # 二级科目
    subject_lv3 = StringField(default=None)             # 三级科目

    init_balance_debit = FloatField()                                           # 期初余额(借方)
    init_balance_credit = FloatField()                                          # 期初余额(贷方)
    cur_amount_debit = FloatField()                                             # 本期发生额(借方)
    cur_amount_credit = FloatField()                                            # 本期发生额(贷方)
    this_year_amount_debit = FloatField(required=True, default=0)               # 本年累计发生额(借方)
    this_year_amount_credit = FloatField(required=True, default=0)              # 本年累计发生额(贷方)
    cur_balance_debit = FloatField(required=True)                               # 期末余额(借方)
    cur_balance_credit = FloatField(required=True)                              # 期末余额(贷方)

    def json(self):
        account_balance_dict = {
            "company_name": self.company_name,
            "is_openning_balance": self.is_openning_balance,
            "date": self.date,
            "subject_lv1": self.subject_lv1,
            "subject_lv2": self.subject_lv2,
            "subject_lv3": self.subject_lv3,
            "init_balance_debit": self.init_balance_debit,
            "init_balance_credit": self.init_balance_credit,
            "cur_amount_debit": self.cur_amount_debit,
            "cur_amount_credit": self.cur_amount_credit,
            "this_year_amount_debit": self.this_year_amount_debit,
            "this_year_amount_credit": self.this_year_amount_credit,
            "cur_balance_debit": self.cur_balance_debit,
            "cur_balance_credit": self.cur_balance_credit,
        }
        return account_balance_dict

    meta = {
        "indexes": ["date", "company_name", "subject_lv1", "subject_lv2", "subject_lv3"]
    }

class Acctid(Document):
    """科目代码"""
    company_name = StringField(required=True)   # 公司名称
    acctid = StringField(required=True)         # 科目代码
    acct_name = StringField(required=True)      # 科目名称
    acct_type = StringField()                   # 科目类别
    balance_direction = StringField()           # 余额方向
    def json(self):
        acct_data = {
            "company_name": self.company_name,
            "acctid": self.acctid,
            "acct_name": self.acct_name,
            "acct_type": self.acct_type,
            "balance_direction": self.balance_direction,
        }
        return acct_data

    meta = {
        "indexes": ["acctid", "company_name"]
    }



# 保存
# BankStatement(
#     object_account="32001766436059555777",
#     object_name="江苏康健医疗用品有限公司",
#     outcome=2040,
#     balance=193591.73,
#     # haha="haha"
# ).save()

# 获取唯一匹配结果，且仅返回单一document，而非列表
# bank_statement = BankStatement.objects(object_account='32001766436059555777').get()
# print(bank_statement.json())

if __name__ == '__main__':
    b = Bank(bankname="测试银行", starting_line=1, content_sheet=1, operation_time_col=1,
             object_account_col=1, object_name_col=1, outcome_col=1, income_col=1,
             balance_col=1, abstract_col=1).save()

    # bank_statement = BankStatement.objects(object_account='32001766436059555777')
    #
    # for i in bank_statement:
    #     print(i)
    #     pprint(i.json())