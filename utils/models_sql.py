from pprint import pprint
from peewee import *


db = MySQLDatabase('Accounting', user='accounting', password='accounting', host='192.168.50.30', port=3306)

db.connect()


class BaseModel(Model):
    class Meta:
        database = db  # 将实体与数据库进行绑定


class Bank(BaseModel):
    bankname = CharField(unique=True, null=False)
    bankcode = IntegerField(unique=True)
    starting_row = IntegerField(null=False)
    ending_row = IntegerField(null=False)
    content_sheet = IntegerField(null=False)
    operation_time_col = IntegerField(null=False)
    object_account_col = IntegerField(null=False)
    object_name_col = IntegerField(null=False)
    outcome_col = IntegerField(null=False)
    income_col = IntegerField(null=False)
    balance_col = IntegerField(null=False)
    abstract_col = IntegerField(null=False)
    xlsx_dir = CharField(unique=True)


class BankStatement(BaseModel):
    company_name = CharField(null=False)       # 所属企业名
    operation_time = DateTimeField(null=False)   # 交易时间
    object_account = CharField(default="")        # 对方账号
    object_name = CharField(default="")           # 对方户名
    outcome = DoubleField(default=0.)                 # 支出
    income = DoubleField(default=0.)                  # 存入
    balance = DoubleField(null=False)             # 余额
    abstract = CharField(null=False)           # 摘要
    bank = CharField(null=False)               # 所属银行
    insert_time = DateTimeField(null=False)      # 写入时间


class Invoice(BaseModel):
    company_name = CharField(null=False)           # 公司名称
    invoice_code = CharField(null=False)           # 发票代码
    invoice_num = CharField(null=False)            # 发票号码
    object_name = CharField(null=True)                         # 购方企业名称
    object_tax_num = CharField(null=True)                      # 购方税号
    bank_account = CharField(null=True)                        # 银行账号
    billing_date = DateTimeField(null=False)         # 开票日期
    merchandise_name = CharField(null=True)                    # 商品名称
    merchandise_amount = IntegerField(null=True)                     # 数量
    unit_price = FloatField(null=True)                           # 单价
    sum_price = DoubleField(null=False)               # 金额
    tax_rate = FloatField(null=True)                             # 税率
    tax = FloatField(null=False)                     # 税额
    tax_category_code = CharField(null=True)                   # 税收分类编码
    invoice_type = CharField(null=False)           # 发票类型（销项发票、进项发票等）
    select_date = DateTimeField(null=True)                       # 勾选日期
    belong_date = DateTimeField(null=True)                       # 所属月份


class InitialOpenningBalance(BaseModel):
    """开账期初数"""
    company_name = CharField(null=False)                       # 公司名称
    object_name = CharField(null=False)                        # 科目名称
    debita_init_openning_balance = FloatField(null=False)        # 借方开账期初数
    fidem_init_openning_balance = FloatField(null=False)         # 贷方开账期初数
    first_grade = CharField(null=False)                        # 期初数一级科目 （应付账款、预付账款、等等）
    open_date = DateTimeField()                                     # 开账日期 （年月）


class VoucherRow(BaseModel):
    """凭证每一行foreign key"""
    index_0 = CharField(default='')
    index_1 = CharField(default='')
    index_2 = CharField(default='')
    index_3 = CharField(default='')
    index_4 = CharField(default='')
    index_5 = CharField(default='')
    index_6 = DoubleField(default='')
    index_7 = DoubleField(default='')


class Voucher(BaseModel):
    """凭证"""
    company_name = CharField(null=False)   # 本公司名称
    specific = CharField(null=False)       # 凭证具体所属事项（进/销目标、其他费用、现金等）
    date = DateTimeField(null=False)         # 凭证所属日期
    category = CharField(null=False)       # 凭证类型
    number = CharField(null=True)                      # 凭证号
    method = CharField(null=True)                      # 收、付、转
    supervisor = CharField(null=True)                  # 主管
    reviewer = CharField(null=True)                    # 审核
    cashier = CharField(null=True)                     # 出纳
    producer = CharField(null=True)                    # 制单
    row_1 = ForeignKeyField(VoucherRow, null=True, default=None, backref='voucher', on_delete='CASCADE')       # 第一行
    row_2 = ForeignKeyField(VoucherRow, null=True, default=None, backref='voucher', on_delete='CASCADE')       # 第二行
    row_3 = ForeignKeyField(VoucherRow, null=True, default=None, backref='voucher', on_delete='CASCADE')       # 第三行
    row_4 = ForeignKeyField(VoucherRow, null=True, default=None, backref='voucher', on_delete='CASCADE')       # 第四行
    row_5 = ForeignKeyField(VoucherRow, null=True, default=None, backref='voucher', on_delete='CASCADE')       # 第五行
    row_6 = ForeignKeyField(VoucherRow, null=True, default=None, backref='voucher', on_delete='CASCADE')       # 第六行
    row_7 = ForeignKeyField(VoucherRow, null=True, default=None, backref='voucher', on_delete='CASCADE')       # 第七行
    row_8 = ForeignKeyField(VoucherRow, null=True, default=None, backref='voucher', on_delete='CASCADE')       # 第八行
    row_9 = ForeignKeyField(VoucherRow, null=True, default=None, backref='voucher', on_delete='CASCADE')       # 第九行


class AccountBalance(BaseModel):
    """科目余额表"""
    company_name = CharField(null=False)           # 公司名称
    is_openning_balance = BooleanField(null=False)   # 是否开账余额
    date = DateTimeField(null=False)                 # 所属日期
    subject_lv1 = CharField(null=False)            # 一级科目
    subject_lv2 = CharField(default=None, null=True)             # 二级科目
    subject_lv3 = CharField(default=None, null=True)             # 三级科目

    init_balance_debit = FloatField(null=True)                                           # 期初余额(借方)
    init_balance_credit = FloatField(null=True)                                          # 期初余额(贷方)
    cur_amount_debit = FloatField(null=True)                                             # 本期发生额(借方)
    cur_amount_credit = FloatField(null=True)                                            # 本期发生额(贷方)
    this_year_amount_debit = FloatField(null=False, default=0)               # 本年累计发生额(借方)
    this_year_amount_credit = FloatField(null=False, default=0)              # 本年累计发生额(贷方)
    cur_balance_debit = FloatField(null=False)                               # 期末余额(借方)
    cur_balance_credit = FloatField(null=False)                              # 期末余额(贷方)


class Acctid(BaseModel):
    """科目代码"""
    company_name = CharField(null=False)   # 公司名称
    acctid = CharField(null=False)         # 科目代码
    acct_name = CharField(null=False)      # 科目名称
    acct_type = CharField()                   # 科目类别
    balance_direction = CharField()           # 余额方向



if __name__ == '__main__':
    # b = Bank(bankname="测试银行", starting_line=1, content_sheet=1, operation_time_col=1,
    #          object_account_col=1, object_name_col=1, outcome_col=1, income_col=1,
    #          balance_col=1, abstract_col=1).save()

    # bank_statement = BankStatement.objects(object_account='32001766436059555777')
    #
    # for i in bank_statement:
    #     print(i)
    #     pprint(i.json())
    # 查询数据库是连接
    print(db.is_closed())  # 返回false未连接
    # 连接数据库
    # Bank.create_table()
    # BankStatement.create_table()
    # Invoice.create_table()
    # InitialOpenningBalance.create_table()
    VoucherRow.create_table()
    Voucher.create_table()
    # AccountBalance.create_table()
    # Acctid.create_table()
    from playhouse.shortcuts import model_to_dict
    # vrs = VoucherRow.get()
    # pprint([vr.voucher.dict() for vr in vrs])
