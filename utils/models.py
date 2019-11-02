from pprint import pprint
from mongoengine import *

connect('accounting', username='hjw', password='newton123')

class BankStatement(Document):
    operation_time = DateTimeField()                # 交易时间
    object_account = StringField(required=True)     # 对方账号
    object_name = StringField()                     # 对方户名
    outcome = FloatField(default=0)                 # 支出
    income = FloatField(default=0)                  # 存入
    balance = FloatField(required=True)             # 余额
    abstract = StringField()                        # 摘要
    bank = ReferenceField()                         # 所属银行

    def json(self):
        bank_statement_dict = {
            "operation_time": self.operation_time,
            "object_account": self.object_account,
            "object_name": self.object_name,
            "outcome": self.outcome,
            "income": self.income,
            "balance": self.balance,
            "abstract": self.abstract
        }
        return bank_statement_dict

    meta = {
        "indexes": ["operation_time", "object_name", "balance"],
        "ordering": ["-operation_time"]
    }

class Bank(Document):
    starting_line = IntField()
    content_sheet = IntField()
    operation_time_col = IntField()


class Invoice(Document):
    pass

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

    bank_statement = BankStatement.objects(object_account='32001766436059555777')

    for i in bank_statement:
        print(i)
        pprint(i.json())