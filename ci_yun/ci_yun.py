# !/usr/bin/python3
# coding=utf-8
# @Time   : 2019/2/22/0022 10:30:21
# Author  : little star
# Func: 词云
import os
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from scipy.misc import imread


def single():
    file_path = os.path.dirname(__file__)
    file_path = os.path.join(file_path, "words.txt")
    with open(file_path, "r", encoding="utf8") as read_obj:
        content = read_obj.read()
    print(content)

    # wordcloud = WordCloud().generate(content)
    # plt.imshow(wordcloud, interpolation="bilinear")
    # plt.axis("off")

    wordcloud = WordCloud(max_font_size=40).generate(content)
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()


def single_word():
    text = "周星晟郭云"
    text = jieba.cut(text)
    text = " ".join(text)

    # x, y = np.ogrid[:300, :300]
    # mask = (x - 150) ** 2 + (y - 150) ** 2 > 130 ** 2
    # mask = 255 * mask.astype(int)

    # 背景样式
    mask = imread("heart.jpg")

    wc = WordCloud(font_path="./FZZJ.TTF", background_color="white", repeat=True, mask=mask)
    wc.generate(text)
    wc.to_file("word.png")

    plt.axis("off")
    plt.imshow(wc, interpolation="bilinear")
    plt.show()


if __name__ == '__main__':
    # single()
    single_word()
    pass
