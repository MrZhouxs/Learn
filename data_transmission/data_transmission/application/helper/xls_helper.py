#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

import xlrd


class XlsHelper(object):
    def __init__(self, excel_path):
        # 设置excel编码格式
        xlrd.Book.encoding = "utf8"
        self.excel_object = self.open_excel(excel_path)

    def open_excel(self, excel_path):
        try:
            if not os.path.isfile(excel_path):
                print(u"文件不存在，请检查文件路径:{}".format(excel_path))
                return None
            book = xlrd.open_workbook(excel_path)
            return book
        except Exception as ex:
            print(u"打开{}Excel表时发生异常，异常原因为:{}".format(excel_path, str(ex)))
        return None

    def open_sheet(self):
        sheet = None
        if self.excel_object:
            try:
                # 获取所有sheet
                # sheets = self.excel_object.sheets()
                # if sheets:
                #     for sheet in sheets:
                #         pass
                # 根据index获取sheet
                sheet = self.excel_object.sheet_by_index(0)
                # 根据sheet的名字获取sheet
                # sheet = self.excel_object.sheet_by_name(u"采集器")
                return sheet
            except Exception as ex:
                print(u"获取Excel的sheet发生异常，异常原因为:{}".format(str(ex)))
        return sheet

    def func(self):
        sheet = self.open_sheet()
        # 获取行数
        rows = sheet.nrows
        print(u"行数为:{}".format(rows))
        # 获取列数
        cols = sheet.ncols
        print(u"列数为:{}".format(cols))
        # 获取标题(获取第一行数据)
        title = sheet.row_values(0)
        print(u"标题为:{}".format(title))
        print("去除第一行数据")
        for i in range(1, rows):
            print(sheet.row_values(i))


if __name__ == '__main__':
    obj = XlsHelper(excel_path="/opt/test.xlsx")
    obj.func()
