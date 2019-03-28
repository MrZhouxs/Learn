#!/usr/bin/python3
# -*- coding: utf-8 -*-

import websocket


class PythonWebSocket(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.ws = None

    def on_message(self, message):
        print(message)

    def on_error(self, error):
        print(error)

    def on_close(self):
        print("***** closed ****")

    def on_open(self):
        print("%%%%% open %%%%%")

    def run(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("ws://{}:{}/websocket".format(self.host, self.port),
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever()

    # def __del__(self):
    #     if self.ws:
    #         self.ws.close()


if __name__ == '__main__':
    host = "127.0.0.1"
    port = 8888
    ws = PythonWebSocket(host, port)
    ws.run()

