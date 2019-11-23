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
            "abstract_col": self.abstract_col
        }
        return bank_dict

    meta = {
        "indexes": ["bankname"]
    }

class BankStatement(Document):
    company_name = StringField(required=True)       # 所属企业名
    operation_time = DateTimeField()                # 交易时间
    object_account = StringField(required=True)     # 对方账号
    object_name = StringField()                     # 对方户名
    outcome = FloatField(default=0)                 # 支出
    income = FloatField(default=0)                  # 存入
    balance = FloatField(required=True)             # 余额
    abstract = StringField()                        # 摘要
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
            "bank": self.bank
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
            "tax_category_code": self.tax_category_code
        }
        return invoice_dict

    meta = {
        "indexes": ["invoice_code"]
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