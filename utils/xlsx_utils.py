import os
import xlrd

class Xlsx():
    def __init__(self, filepath, sheet_index=0):
        self.sheet = self.read_xlsx(filepath, sheet_index)

    def read_xlsx(self, filepath, sheet_index=0):
        data = xlrd.open_workbook(filepath)
        table = data.sheet_by_index(sheet_index)
        return table

    def contents(self, row_start=0, row_end=None, end_before_last_row=None):
        """

        :param row_start: 开始行
        :param row_end: 指定结束行
        :param end_before_last_row: 倒数第几行结束，最后剩下多少行要舍弃！
        :return:
        """
        #优先级：end_before_last_row > row_end，都不填默认是所有行。
        if not row_end:
            row_end = self.sheet.nrows
        if end_before_last_row:
            row_end = self.sheet.nrows - end_before_last_row

        for i in range(row_start, row_end, 1):
            yield self.sheet.row_values(i)



if __name__ == '__main__':
    xl = Xlsx("D:\workspace\Accounting\input/bankstatements\建设银行/201908-南建.xls")
    for i in xl.contents(row_start=0, end_before_last_row=1):
        print(i)