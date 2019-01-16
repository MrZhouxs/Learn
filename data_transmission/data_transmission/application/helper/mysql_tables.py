#!/usr/bin/python3
# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, MetaData
from sqlalchemy import String, BigInteger, Text, Integer, DateTime
from data_transmission.sdk.db import DBBase


metadata = MetaData()

# 用来存储数据发送是否成功，默认为失败为0
transmission_exception = Table("transmission_exception", metadata,
                               Column("id", BigInteger, primary_key=True, autoincrement=True),
                               Column("task_id", String(64), default=""),
                               Column("send_params", Text),
                               Column("typeof", String(16)),
                               Column("is_success", Integer, default="0"),    # 1成功 0失败
                               Column("source", String(16))                   # 标记是发送端还是接收端
                               )

software_update = Table("software_update", metadata,
                        Column("id", BigInteger, primary_key=True, autoincrement=True),
                        Column("version", String(255)),
                        Column("path", String(255)),
                        Column("upload_time", DateTime),
                        Column("publish_time", DateTime),
                        Column("soft_state", String(255)),
                        Column("jhi_size", String(255)),
                        Column("jhi_desc", String(255)),
                        Column("is_publish", Integer),
                        Column("is_done", Integer),
                        Column("server_name", String(64)),
                        Column("is_update", Integer),
                        Column("remarks_1", Integer),
                        Column("remarks_2", Integer),
                        Column("remarks_3", String(255)),
                        Column("remarks_4", String(255)),
                        Column("server_information_id", BigInteger)
                        )


# class SoftwareUpdate(DBBase):
#     __tablename__ = "software_update"
#     id = Column(BigInteger, primary_key=True, autoincrement=True),
#     version = Column(String(255)),
#     path = Column(String(255)),
#     upload_time = Column(DateTime),
#     publish_time = Column(DateTime),
#     soft_state = Column(String(255)),
#     jhi_size = Column(String(255)),
#     jhi_desc = Column(String(255)),
#     is_publish = Column(Integer),
#     is_done = Column(Integer),
#     server_name = Column(String(64)),
#     is_update = Column(Integer),
#     remarks_1 = Column(Integer),
#     remarks_2 = Column(Integer),
#     remarks_3 = Column(String(255)),
#     remarks_4 = Column(String(255), default=""),
#     server_information_id = Column(BigInteger)
