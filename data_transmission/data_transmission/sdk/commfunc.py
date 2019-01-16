#! /usr/env/bin python
# -*- encoding:utf-8 -*-
import uuid
import os
import socket
import fcntl
import struct

def get_id(server_name):
    '''
    get unique serverid func.

    :param server_name: server name.
    :return: server_id
    '''
    id = ''
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    id_file_full_path = '{}/{}_id'.format(path, server_name)
    if os.path.exists(id_file_full_path):
        with open(id_file_full_path, 'rb') as f:
            id = f.read()
            if id:
                id = id.decode('utf-8')
    else:
        id = str(uuid.uuid4()).upper()

        with open(id_file_full_path, 'wb') as f:
            f.write(id.encode('utf-8'))
    return id

def execut_cmd(cmd):
    return os.popen(cmd)

def get_host_macs():
    '''

    :return:{'eth4': '00:0C:29:F6:A3:FD',}
    '''
    eth_macs = dict()
    eth = execut_cmd("ifconfig | grep HWaddr |awk '{print $1}'").read()
    eths = eth.split('\n')
    mac = execut_cmd("ifconfig | grep HWaddr |awk '{print $5}'").read()
    macs = mac.split('\n')
    for each_eth, each_mac in zip(eths,macs):
        if not each_eth or not each_mac:
            continue
        eth_macs[each_eth] = each_mac
    return eth_macs


def get_eth_ip(ifname):
    '''

    :param ifname: 网卡名
    :return: ip
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = None
    try:
        ip = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', bytes(ifname[:15].encode('utf-8')))
        )[20:24])
    except:
        print('get ip failed!')

    return ip


def get_macs_ips():
    '''

    :return: {'eth4': ['00:0C:29:F6:A3:FD', '192.168.31.208'],}
    '''
    macs_and_ips = dict()
    macs = get_host_macs()
    for ifname in macs:
        ip = get_eth_ip(ifname)
        macs_and_ips[ifname] = [macs[ifname], ip]
    return macs_and_ips
