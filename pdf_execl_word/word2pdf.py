# !/usr/bin/python3
# coding=utf-8
# @Time   : 2019/3/1/0001 16:19:42
# Author  : little star
"""
适用于Windows，64位Windows和Windows CE
"""
import os
import comtypes.client
from pythonShell import Singleton

PDF_SUFFIX = ".pdf"
# word文档转化为pdf文档时使用的格式为17
WORD_FORMAT_PDF = 17
# ppt文档转化为pdf文档时使用的格式为32


class Word2Pdf(Singleton):
    def __init__(self):
        super(Word2Pdf, self).__init__()

    def word2pdf(self, doc, pdf=None):
        """
        将word转换成pdf
        :param doc: word文档的文件路径或者是包含word文档的文件夹路径
        :type doc: str | list
        :param pdf: 如给出，则输出的pdf文件与之一一对应，如不给出，默认word文件名作为pdf的文件名
        :type pdf: str | list
        :return:
        """
        if os.path.isdir(doc):
            file_path = self.walk_path(doc, "f", include=[".doc", ".docx"])
        else:
            file_path = [doc]
        if pdf:
            if not isinstance(pdf, (list, tuple)):
                pdf = [pdf]

        for index in range(len(file_path)):
            doc_path = file_path[index]
            doc_dir = os.path.dirname(doc_path)
            if pdf:
                out_pdf_path = pdf[index]
                if os.path.split(out_pdf_path)[0]:
                    out_pdf_path = out_pdf_path
                else:
                    pdf_file_name = self.get_file_name(out_pdf_path)
                    pdf_file_name += PDF_SUFFIX
                    out_pdf_path = os.path.join(doc_dir, pdf_file_name)
            else:
                doc_file_name = self.get_file_name(doc_path)
                pdf_file_name = doc_file_name + PDF_SUFFIX
                out_pdf_path = os.path.join(doc_dir, pdf_file_name)
            # 如果pdf已存在，则先删除
            if os.path.isfile(out_pdf_path):
                os.remove(out_pdf_path)
            try:
                doc = comtypes.client.CreateObject('Word.Application')
                word = doc.Documents.Open(doc_path)
                word.SaveAs(out_pdf_path, FileFormat=WORD_FORMAT_PDF)
            except Exception as ex:
                print(ex)
            finally:
                # 释放内存
                word.close()
                doc.Quit()

    @staticmethod
    def walk_path(path, rtype="f", include=list(), exclude=list()):
        """
        遍历文件夹下所有文件和文件夹
        :param path: 文件夹的路径
        :param rtype: 需要返回的值类型，是返回所有的文件路径，还是所有文件夹路径
        :arg rtype: f, d, a
        :param include: 只返回带有该字段的文件路径
        :type include: str | list | tuple
        :param exclude: 去除带有该字段的文件路径
        :type exclude: str | list | tuple
        :return:
        """
        file_path = list()
        file_dirs = list()
        if not isinstance(include, (list, tuple)):
            include = [include]
        if not isinstance(exclude, (list, tuple)):
            exclude = [exclude]
        for root, dirs, files in os.walk(path):
            if files:
                for file in files:
                    temp_file_path = os.path.join(root, file)
                    if include is None and exclude is None:
                        file_path.append(temp_file_path)
                    elif include is not None and exclude is not None:
                        for each in include:
                            if file.find(each) != -1:
                                file_path.append(temp_file_path)
                        for each in exclude:
                            if file.find(each) != -1:
                                file_path.remove(temp_file_path)
                    elif include:
                        for each in include:
                            if file.find(each) != -1:
                                file_path.append(temp_file_path)
                    elif exclude:
                        for each in exclude:
                            if file.find(each) != -1:
                                file_path.remove(temp_file_path)
            if dirs:
                for _dir in dirs:
                    file_dirs.append(os.path.join(root, _dir))
        # 去除重复数据
        file_path = list(set(file_path))
        file_dirs = list(set(file_dirs))
        rtype = rtype.lower()
        result = None
        if rtype == "f":
            result = file_path
        elif rtype == "d":
            result = file_dirs
        elif rtype == "a":
            result = file_path, file_dirs
        return result

    @staticmethod
    def get_file_name(path):
        file_name = os.path.split(path)[-1].split(".")[0]
        return file_name


if __name__ == '__main__':
    # word2pdf("D:\Demos\pythonWorkSpace\pythonShell\pythonShell\pdf_execl_word/tt.docx", "./11.pdf")
    a = Word2Pdf()
    a.word2pdf("D:\Demos\pythonWorkSpace\pythonShell\pythonShell\pdf_execl_word")
