# -*- encoding:utf-8 -*-
from setuptools import setup, find_packages
setup(
    name="data_transmission",
    version="1.0.1",
    packages = find_packages(),     # 会自动查找当前目录下的所有模块(.py文件) 和包(包含__init___.py文件的文件夹)
    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    package_data = {
        # 任何包中含有.txt文件，都包含它
        # '': ["txt"],
        #  包含src包etc文件夹中的 *.ini *.conf文件
        '': ['etc/*.ini', 'etc/*.conf', "etc/*.json", "lib/*.*", "etc/*.*"],
    },
    #
    install_requires=[],
    entry_points={
        'console_scripts': [
            'data_transmission = data_transmission.application.start:run',
            # 'bar = demo:test',
        ],
        'gui_scripts': [
           # 'baz = demo:test',
        ]
    },
    # metadata for upload to PyPI
    # author = "Me",
    # author_email = "me@example.com",
    # description = "This is an Example Package",
    # license = "PSF",
    # keywords = "hello world example examples",

)
""
install_requires = [
        "pbr>=0.5.21",
        "pam>=0.1.4",
        "WebOb>=1.2.3,<1.3",
        "eventlet>=0.13.0",
        "greenlet>=0.3.2",
        "PasteDeploy>=1.5.0",
        "Paste",
        "Routes>=1.12.3,!=2.0",
        "passlib",
        "iso8601>=0.1.8",
        "oslo.config>=1.2.0",
        "Babel>=1.3",
        "itsdangerous",
        "oslo_serialization",
        "msgpack>=0.4.0",
        "pytz>2013.6",
        "oslo.utils>=3.18.0",
        "pyparsing>=2.0.7",
        "netaddr>=0.7.13,!=0.7.16",
        "oslo.log>=3.19.0",
        "pika>=0.10.0",
        "config>=0.3.9",
        "schedule",
    ],       # 常用
""
