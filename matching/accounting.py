# -*- coding:utf-8 -*-
# Author: 黄景文

import os
import xlrd
import datetime
from .configs import *

class accounting:
    '发票-银行对账单自动化匹配工具'
    empCount = 0

    def __init__(self):
        self.FAPIAO_DIR = FAPIAO_DIR
        self.YINHAGN_DIR = YINHAGN_DIR
        self.FAPIAO_SET = []
        self.YINHAGN_SET = []
        self.MATCH_SET = []

    @staticmethod
    def open_excel(file='file.xls'):
        try:
            data = xlrd.open_workbook(file)
            return data
        except Exception as e:
            print(str(e))

    def loadExcel(self, file_name, start_row=0):

        data = self.open_excel(file=file_name)
        table = data.sheet_by_index(0)  # 通过索引顺序获取

        data_set = []
        for i in range(start_row, table.nrows):
            attribute = table.row_values(start_row - 1)
            row = table.row_values(i)
            row_data = {attribute[i]: row[i] for i in range(len(attribute))}
            data_set.append(row_data)
            # table.row_values(i)
        return data_set

    def loadFaPiao(self):
        for i in os.listdir(FAPIAO_DIR):
            if i.startswith('~$'):
                # 判断是否因为excel文件打开而出现的中间文件
                continue

            path = os.path.join(FAPIAO_DIR, i)
            print(path)
            self.FAPIAO_SET += self.loadExcel(file_name=path, start_row=3)

        return

    def loadYinHang(self):
        for i in os.listdir(YINHAGN_DIR):
            if i.startswith('~$'):
                # 判断是否因为excel文件打开而出现的中间文件
                continue

            path = os.path.join(YINHAGN_DIR, i)
            print(path)

            yinhang_data = self.loadExcel(file_name=path, start_row=11)
            yinhang_data = yinhang_data[:-3]

            self.YINHAGN_SET += [i for i in yinhang_data if i[u"对方户名"] and i[u"支出"]]

        return

    def match(self):
        self.loadFaPiao()
        self.loadYinHang()

        companies_fp = list(set([i[u"销方名称"] for i in self.FAPIAO_SET]))
        print(len(companies_fp), type(companies_fp))

        for corp in companies_fp:
            company_data = {'matched': [], 'fapiao_unmatched': [], 'yinhang_unmatched': []}

            match_yh = self.filter_by_corp(u"对方户名", corp, self.YINHAGN_SET)
            match_fp = self.filter_by_corp(u"销方名称", corp, self.FAPIAO_SET)
            fp_rm_list = []


            print(corp)

            # 开始生成匹配数据
            for i in range(len(match_fp)):
                match_info = {u"开票日期": u"", u"开票单位": u"", u"发票号码": u"", u"增值税发票金额": u"", u"汇款日期": u"", u"汇款金额": u"", u"已付": u"否"}

                fp_prize = float(match_fp[i][u"金额"]) + float(match_fp[i][u"税额"])  # 计算发票金额

                print(match_fp, '@@@')

                for yh in match_yh:
                    if float(yh[u"支出"]) == fp_prize:
                        # print u"发票：", fp[u"销方名称"], fp_prize
                        # print u"银行票：",yh[u"对方户名"], yh[u"支出"]
                        match_info[u"开票日期"] = match_fp[i][u"确认/认证日期"]
                        match_info[u"开票单位"] = match_fp[i][u"销方名称"]
                        match_info[u"发票号码"] = match_fp[i][u"发票号码"]
                        match_info[u"增值税发票金额"] = fp_prize
                        match_info[u"汇款日期"] = self.translate_date(yh[u"交易时间"])
                        match_info[u"汇款金额"] = yh[u"支出"]
                        match_info[u"已付"] = u"是"

                        self.MATCH_SET.append(match_info)

                        match_yh.remove(yh)
                        fp_rm_list.append(match_fp[i])
                        # match_fp.remove(fp)
                        # company_data['matched'].append()

                        for k, v in match_info.items():
                            print(k, v)
                        print("===")

            match_fp = [i for i in match_fp if i not in fp_rm_list]

            for yh in match_yh:
                print(u"银行票：", yh[u"对方户名"], yh[u"支出"], " not mateched TAT")
                match_info = {u"开票日期": u"", u"开票单位": yh[u"对方户名"], u"发票号码": u"", u"增值税发票金额": u"", u"汇款日期": self.translate_date(yh[u"交易时间"]), u"汇款金额": yh[u"支出"],
                              u"已付": u"否"}
                self.MATCH_SET.append(match_info)

            for fp in match_fp:
                fp_prize = float(fp[u"金额"]) + float(fp[u"税额"])
                print(u"发票：", fp[u"销方名称"], float(fp[u"金额"]) + float(fp[u"税额"]), " not mateched TAT")
                match_info = {u"开票日期": fp[u"开票日期"], u"开票单位":fp[u"销方名称"], u"发票号码": fp[u"发票号码"], u"增值税发票金额": fp_prize, u"汇款日期": u"", u"汇款金额": u"",
                              u"已付": u"否"}
                self.MATCH_SET.append(match_info)

                pass

            self.MATCH_SET.append({u"开票日期": u"", u"开票单位": u"", u"发票号码": u"", u"增值税发票金额": u"", u"汇款日期": u"", u"汇款金额": u"", u"已付": u""})

            print('*'*33 )
        return

    @staticmethod
    def filter_by_corp(key, corp, companies_set):
        return filter(lambda i: i[key] == corp, companies_set)

    @staticmethod
    def translate_date(date):
        return datetime.datetime.strftime(datetime.datetime(*xlrd.xldate_as_tuple(date, 0)), '%Y-%m-%d')

