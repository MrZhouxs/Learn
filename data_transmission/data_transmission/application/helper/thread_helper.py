#!/usr/bin/python3
# -*- coding: utf-8 -*-
import threading


def start_thread(func, *args):
    if args:
        thread = threading.Thread(target=func, args=(args, ))
    else:
        thread = threading.Thread(target=func)
    thread.start()
