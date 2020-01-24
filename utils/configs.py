import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

BALANCE_SHEET_MODEL = os.path.join(PROJECT_ROOT, "xlsx_model/资产负债表.xlsx")

# 开账期初数科目分类
# 只有一级科目
SINGLE_GRADE = ['现金', '应付工资', '实收资本', '本年利润', '主营业务收入',
                '营业外收入', '主营业务成本', '所得税']
# 有一级科目和二级科目
DOUBLE_GRADE = ['银行存款', '应收账款', '预付账款', '其他应收款', '库存商品',
                '固定资产', '累计折旧', '应付账款', '应交税费', '其他应付款',
                '盈余公积', '利润分配', '主营业务税金及附加', '营业费用', '管理费用', '财务费用']
