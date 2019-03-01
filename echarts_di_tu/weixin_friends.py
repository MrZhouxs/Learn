# !/usr/bin/python3
# coding=utf-8
# @Time   : 2019/2/22/0022 17:05:11
# Author  : little star
# Func: 显示微信好友分布图
import itchat
import collections
from pyecharts import Geo
from pyecharts.datasets.coordinates import DefaultChinaDataBank


class WeiXin(object):
    def __init__(self):
        self.coordinate = list()
        self.parse_coordinate()
        self.login()
        pass

    def login(self):
        # 使用热启动
        itchat.auto_login()
        itchat.login()

    def parse_coordinate(self):
        coordinates = DefaultChinaDataBank().get_cities_in_region(region="CN")
        for coordinate in coordinates.keys():
            self.coordinate.append(coordinate)

    def friends(self):
        cities = list()
        users = itchat.get_friends(update=True)
        for user in users:
            city = user.get("City")
            if city:
                if city in self.coordinate:
                    cities.append(city)
                else:
                    for coordinate in self.coordinate:
                        if city in coordinate:
                            cities.append(coordinate)
                            break
                    else:
                        print("{}不在统计范围内".format(city))
        result = self.count(cities)
        return result

    def count(self, data=None):
        result = list()
        if data:
            counts = collections.Counter(data)
            for city, num in counts.items():
                if city:
                    temp = (city, num)
                    result.append(temp)
        return result

    def visual_map(self):
        geo = Geo("微信好友分布图", "data from weixin", title_color="#fff",
                  title_pos="center", width=1000,
                  height=600, background_color='white')
        attr, value = geo.cast(self.friends())
        geo.add("", attr, value, visual_range=[0, 200], maptype='china', visual_text_color="#fff",
                symbol_size=10, is_visualmap=True)
        geo.render("chat_friends.html")


if __name__ == '__main__':
    wx = WeiXin()
    wx.visual_map()
