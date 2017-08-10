# !/usr/bin/python2.7
# coding=utf-8
# @Time    : 2017/8/10 13:56
# Author   : pushi_time
# @File    : mongodb.py
# Function : mongodb的使用细节

"""
(>) 大于 - $gt
(<) 小于 - $lt
(>=) 大于等于 - $gte
(<= ) 小于等于 - $lte

db是数据库，table是集合（表）
db.table.find({},{"title":1,_id:0}).sort().skip(10).limit(100)
当查询时同时使用sort,skip,limit，无论位置先后，最先执行顺序 sort再skip再limit。
find参数含义：第一个 {} 放 where 条件，为空表示返回集合中所有文档。
            第二个 {} 指定那些列显示和不显示 （0表示不显示 1表示显示，不显示的可以省略不写)。
find查询效果：读取从 10 条记录后 100 条记录,即在集合中跳过前面 10 条返回 100 条数据。（11-100）
sort()方法对数据进行排序，sort()方法可以通过参数指定排序的字段，
并使用 1 和 -1 来指定排序的方式，其中 1 为升序排列，而-1是用于降序排列。
"""

import pymongo

database_name = 'push'
table_name = 'table'
class Mongodb:
    def __init__(self):
        # 类似于创建数据库的句柄 connection
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        # 类似于创建数据库 self.db = self.client.database_name
        self.db = self.client[database_name]
        # 类似于创建表，但mongodb里叫创建集合
        self.port = self.db[table_name]

    # 数据入库，data是字典的形式，也可以是list包含字典的形式（[{},{}]）
    def insert_data(self, data):
        self.port.insert(data)

    # 查询数据库，data是字典的形式，结果返回的是list的形式
    def select_data(self, data):
        return self.port.find(data)

    # 删除一条记录记录，data是字典的形式
    def delete_data(self, data):
        # 如果数据库中满足多条记录，会删除所有满足的
        self.port.remove(data)
        # 只会删除一条记录
        self.port.delete_one(data)
        # 同self.port.remove(data)效果一样
        self.port.delete_many(data)     # data同delete_one形式一样，不需要是list

    # 修改记录 old_data,new_data 都是字典的形式
    def update_data(self, old_data, new_data):
        self.port.update_one(old_data, {'$set': new_data}, multi=True)
        self.port.update_many(old_data, {'$set': new_data}, multi=True)

    def __del__(self):
        self.port.drop()
        self.db.drop_collection(database_name)
        self.client.close()