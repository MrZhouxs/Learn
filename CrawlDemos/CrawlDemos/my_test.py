# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time   : 2019/3/28/0028 15:30:14
# Author  : little star
import requests


def get_cookie():
    url = "http://exercise.kingname.info/exercise_login"
    data = {"username": "kingname", "password": "genius", "rememberme": "Yes"}
    response = requests.post(url=url, data=data, allow_redirects=False)
    cookie = response.cookies.get_dict()
    return cookie


def login():
    url = "http://exercise.kingname.info/exercise_login_success"
    cookies = {'__cfduid': 'd293e2456b92a7f9bbf3842f84f60ab7f1554187016', 'remember_token': 'kingname|90c52ed9e8aaf93ee8dc57e1513d4c2e6713c18dc3489c6aa441371de05a57d52fc761bf63983cdd52589b286709e44e1e8efa37bca8fd1c51207bc6379e590e', 'session': '.eJwlzkkOwjAMQNG7eM0ig6f0MlUcO4AQXbSwQtwdEAf4T_8F69zjuMDy2J9xgvXqsIB5Sqx9ZpEgJCte2ZMSZ-PAZlSx1UneTEvqUdwnDcPBnLU7R8M8exZHVcYYGk10VEXp9ZdEzNQqkjKlXkytVPFUhggGfqmAEzyP2P8zt-t23vo94P0B0Gcxvg.D4SUiA.vGVe622qLb_CAtsmYwMl6YvtGtc'}
    response = requests.get(url, cookies=cookies)
    print(response.status_code)
    print(response.text)


if __name__ == '__main__':
    get_cookie()
    login()
