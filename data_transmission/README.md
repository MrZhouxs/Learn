# 数据传输服务
    功能：
    1、每隔10min查询ES的数据，并上报到上级节点，将数据入到ES中。
    2、从本级节点的Kafka中获取告警数据上报到上级节点，录入到上级节点的Kafka中。
    3、下发本级节点的升级信息到下级节点，并下发升级包
    
    备注：
    1、1000条数据，大概12M2
    2、每隔10分钟获取ES数据（时间可配置），ES查询出的数据，1000条生成一个本地文件，数量可配置;
       接收端收到ES的数据，将数据插入到ES，数据原本属于哪个index，还插入到哪个index中
    3、数据发送调用java的jar
    4、MQ队列解释：
    data_transmission_send java向目标节点发送的队列名
    data_transmission_receive java从data_transmission_send中获取数据并将数据发送到data_transmission_receive
    update_queue 升级策略的routing_key(不要更改)
    notice_queue 反馈数据的MQ队列名
    