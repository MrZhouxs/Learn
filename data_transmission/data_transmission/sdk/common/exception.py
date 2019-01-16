"""
implement my exception
"""


class MyError(Exception):
    def __init__(self, *args, **kwargs):
        super(MyError, self).__init__(args, kwargs)
