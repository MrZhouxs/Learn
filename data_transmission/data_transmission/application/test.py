import datetime
import json
import os
import base64
import sys
import time
import queue

from data_transmission.application.helper import get_queue, put_queue
from data_transmission.application.helper.jpype_helper import JpypeHelper
from data_transmission.application.helper.thread_helper import start_thread
from data_transmission.sdk.db import DBOption
from data_transmission.sdk.mq import MQClient

q = queue.Queue()


def file_size():
    file_path = "/opt/tmp/send/b80d0311-5796-4ae9-927a-874181850c8e-2018-12-21-13-44-21.txt"
    size2 = os.path.getsize(file_path)
    if size2 > 1024:
        print(round(size2 / 1024 / 1024, 1))
    print(size2)
    content = ""
    obj = open(file_path, "r")
    while True:
        content_temp = obj.read(1024)
        if content_temp:
            content += content_temp
        else:

            break
    print("seek = ", obj.tell())
    obj.close()
    print(sys.getsizeof(content))


def split_data(data, limit_size=3):
    len_data = len(data)
    number = len_data // limit_size
    print("number = ", number)
    result = list()
    if data:
        if number == 0:
            result.append(data)
        else:
            index = 0
            for index in range(0, number):
                result.append(data[index * limit_size: (index + 1) * limit_size])
            print("index = ", index)
            last_data = data[(index + 1) * limit_size:]
            if last_data:
                result.append(last_data)
    return result


def calculate_digits(digits):
    """
    换算字节大小.
    例： 1KB -> 1024 bytes; 1MB -> 1024*1024 bytes; 1GB -> 1024*1024*1024 bytes.
    :param digits: 需要换算的字节.
    :return int: 以bytes为单位的大小.
    """
    temp_digits = digits[: len(digits) - 1]
    temp_digits = int(temp_digits)
    if "K" in digits or "k" in digits:
        result = temp_digits * 1024
    elif "M" in digits or "m" in digits:
        result = temp_digits * 1024 * 1024
    elif "G" in digits or "g" in digits:
        result = temp_digits * 1024 * 1024 * 1024
    else:
        result = temp_digits
    return result


def calculate_time(time_of_query):
    """
    计算查询ES的时间间隔.
    :param time_of_query: 用户配置的时间.
           时间的格式为： xxx s(S), xxx m(M), xxx (H), xxx d(D)
    :return:
    """
    result = None
    time_string = time_of_query[: len(time_of_query) - 1]
    time_int = int(time_string)
    if "s" in time_of_query or "S" in time_of_query:
        result = time_int
    elif "m" in time_of_query or "M" in time_of_query:
        result = time_int * 60
    elif "h" in time_of_query or "H" in time_of_query:
        result = time_int * 60 * 60
    elif "d" in time_of_query or "D" in time_of_query:
        result = time_int * 60 * 60 * 24
    return result


def send_to_kafka(data, topic, hosts="127.0.0.1:9092"):
    import kafka
    _kafka_producer = kafka.KafkaProducer(bootstrap_servers=hosts)
    try:
        if not isinstance(data, str):
            data = json.dumps(data)
        if not isinstance(data, bytes):
            data = bytes(data, encoding="utf8")
        _kafka_producer.send(topic=topic, value=data)
        time.sleep(2)
        return True
    except Exception as ex:
        print(str(ex))
        print(u"向Kafka的topic为{}发送数据失败".format(topic))
    return False


def query_es():
    es_query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "terms": {
                            "public_field.record_type.keyword": [
                                "second",
                                "minute",
                                "hour"
                            ]
                        }
                    }
                ]
            }
        },
        "size": 10
    }
    from elasticsearch import Elasticsearch
    es = Elasticsearch([{"host": "192.168.0.36", "port": 9200}])
    res = es.search(index="s_cmm*", body=es_query)
    print(res)


class DES(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.encode(encoding="utf8")
        return super(DES, self).default(obj)


def file_test():
    file_path = "/opt/tmp/send_package/ssh_collector-1.0.6.tar.gz"
    with open(file_path, "rb") as obj:
        content = obj.read()
    base64_bytes = base64.b64encode(content)
    base64_string = base64_bytes.decode("utf8")
    try:
        data = {"data": base64_string}
        json_str = json.dumps(data)
    except Exception as ex:
        print(ex)

    json_data = json.loads(json_str)
    with open("/opt/tmp/receive_package/ssh_collector-1.0.6.tar.gz", "ab+") as obj:
        data_temp = json_data.get("data")
        str_file_content = base64.b64decode(data_temp)
        obj.write(str_file_content)


def data_to_es():
    file_path = "/opt/tmp/receive_file/2019-01-08-11-00-08"
    file_name = "2019-01-08-11-00-08_-1.txt"
    from data_transmission.application.helper.elasticsearch_operator import ElasticsearchHelper
    from data_transmission.application.helper.file_operator import FileOperator
    file_obj = FileOperator()
    es_obj = ElasticsearchHelper(es_config={"host": "192.168.0.78", "port": 9200}, db_url="mysql+mysqlconnector://Niord:hardwork@192.168.0.29:3306/six_xx?charset=utf8")
    file_content = file_obj.read_file(file_name, file_path)
    import json
    json_data = json.loads(file_content)
    es_obj.insert_into_es(task_id="1353ff36-8f50-4b5f-b3b7-5f9dea3e118f", data=file_content, send_params=None, source=None, typeof=None)


def get_alarm_data(db_url):
    result = dict()
    sql = "select * from alarm_manage where id=251"
    with DBOption(url=db_url) as session:
        res = session.execute(sql)
    if res.rowcount > 0:
        for row in res:
            for key, val in row.items():
                if key == "id":
                    continue
                if isinstance(val, datetime.datetime):
                    val = str(val)
                result.setdefault(key, val)
    else:
        alarm_data = {"process_wizard": None, "alarm_type": "DEVICE", "alarm_level": "SERIOUS", "alarm_advise": None, "alarm_source": "AUTOMATIC", "process_man": None, "alarm_happen_time": datetime.datetime(2019, 1, 4, 23, 42, 51), "node_id": 1, "process_record": None, "deploy_id": 33, "event_code": "20190104_234702_117544", "alarm_reason": "snmp_实时_cpu使用率告警中，思科内存使用率指标项,由计算得到数值： 25.72, 达到告警指标, 并且持续了1s以上，触发了告警条件", "alarm_start_time": datetime.datetime(2019, 1, 4, 23, 42, 52), "software_allocation_id": None, "alarm_describe": "snmp_实时_cpu使用率告警中，思科内存使用率指标项,由计算得到数值： 25.72, 达到告警指标", "id": 251, "process_time": None, "association_system": None, "alarm_name": "snmp_实时_cpu使用率功能异常发出严重级别告警", "alarm_state": "ALARMING", "alarm_recently_time": datetime.datetime(2019, 1, 4, 23, 42, 52), "remark_1": "4000002", "remark_2": None}
        for key, val in alarm_data.items():
            if key == "id":
                continue
            if isinstance(val, datetime.datetime):
                val = str(val)
            result.setdefault(key, val)
    print(result)
    return result


def test_queue():
    while True:
        data = get_queue()
        if data:
            print(" --------------- queue data is : ---------------------")
            print(data)
            print(type(data))
        else:
            time.sleep(5)
            print("queue is empty")


def puts_queue():
    put_queue({"b": "456"})


def test_mq():
    temp_data = [{'server_name': 'ssh_collector', 'path': 'http://192.168.0.29:18080/api/manual/server-download?servername=ssh_collector&version=1.0.6', 'version': '1.0.6'}]
    temp_data = json.dumps(temp_data)
    MQClient.send_message(url="amqp://admin:123456@192.168.0.78:5672", exchange_name="", routing_key="transmission_update_server", message=temp_data)
    ss = "transmission_update_server"
    print(sys.getsizeof(ss))


if __name__ == '__main__':
    a = {"a": "222", "b": "123"}
    # send_to_kafka(data=a, topic="alarm-data", hosts="192.168.0.29:9092")
    # data_to_es()
    # db_url = "mysql+mysqlconnector://Niord:hardwork@192.168.0.29:3306/six_xx?charset=utf8"
    # alarm_data = get_alarm_data(db_url)
    # send_to_kafka(data=alarm_data, topic="alarm-data", hosts="192.168.0.78:9092")
    test_mq()
