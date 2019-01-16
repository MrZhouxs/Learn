"""zookeeper process package.

all zookeeper process class.

ZkHelp is implement zookeeper option func.
"""
# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
import json

# import schedule
from kazoo.client import KazooClient
from kazoo.client import KazooState
import kazoo
from kazoo.exceptions import NodeExistsError
from kazoo.protocol.states import ZnodeStat


# def update_online(*args, **kwargs):
#     if isinstance(kwargs['this'],CZkHelp):
#         if kwargs['this'].m_isConn == False:
#             if kwargs['this'].init_zk():
#                 kwargs['this'].m_isConn = True
#         else:
#             kwargs['this'].update_node_time()
from kazoo.recipe.watchers import DataWatch, ChildrenWatch

from ..sdk.common.exception import MyError


class ZkHelp(object):
    """zookeeper option class.

    zookeeper client implement, you can connect zookeeper,
    add node and add node data.

    Attributes:
        zk_hosts: hosts info.
        m_node: my node info.
        m_isActive: is active
        m_isConn: is connected
        m_zk: zookeeper client instance
    """

    def __init__(self, hosts='127.0.0.1:2181'):
        """init func.

        :param str hosts: zookeeper servers, 多个host使用;连接.
        """
        self.zk_hosts = hosts
        self.m_node = dict()
        self.m_isActive = False
        self.m_isConn = False
        self.m_zk = None
        if self.init_zk():
            self.m_isConn = True
        # schedule.every(30).seconds.do(update_online,this=self).tag('KeepOnline')
        self.m_zk

    def __del__(self):
        """delete func implement."""
        # schedule.clear('KeepOnline')

        self.m_zk.close()
    def stop_zk(self):
        self.m_zk.stop()
        self.m_zk.close()
    def init_zk(self):
        """init zookeeper client.

        create client and connect to zookeeper server.

        :return: is connect success
        """
        try:
            # if is connected, stop it
            # if hasattr(self, 'm_zk'):
            if self.m_zk:
                self.m_zk.stop()

            # create new connection to zookeeper server, use kazoo package
            self.m_zk = KazooClient(hosts=self.zk_hosts,
                                    connection_retry={'max_tries': -1, 'max_delay': 2})
            # listen this
            self.m_zk.add_listener(self.my_listener)
            # start it
            #self.m_zk.start(timeout=2)

            # self.m_zk.get_children('/soc/MonitorServer_master', testy)
            # ChildrenWatch
            # DataWatch(client=self.m_zk, path='/soc/MonitorServer_master', func=testy)
            #
            # @self.m_zk.DataWatch('/soc/MonitorServer_master')
            # def test(data, stat):
            #     print("-----------------------------zk:", data, stat)

            return True
        except Exception as ex:
            print("Error:", ex)
            #raise MyError(ex)

    def start(self):
        self.m_zk.start(timeout=2)

    def my_listener(self, state):
        """ listener implement func.

        listen and option connection.

        :param state: current connection state
        """
        if state == KazooState.LOST:
            self.m_isActive = False
            print("LOST")
        elif state == KazooState.SUSPENDED:
            self.m_isActive = False
            print("SUSPENDED")
        else:
            self.m_isActive = True
            print("Connected")

    def add_node(self, path, value=None, ephemeral=False, sequence=False):
        """add new node to zookeeper server.

        Create a node with the given value as its data. Optionally
        set an ACL on the node.

        The ephemeral and sequence arguments determine the type of the
        node.

        An ephemeral node will be automatically removed by ZooKeeper
        when the session associated with the creation of the node
        expires.

        A sequential node will be given the specified path plus a
        suffix `i` where i is the current sequential number of the
        node. The sequence number is always fixed length of 10 digits,
        0 padded. Once such a node is created, the sequential number
        will be incremented by one.

        If a node with the same actual path already exists in
        ZooKeeper, a NodeExistsError will be raised. Note that since a
        different actual path is used for each invocation of creating
        sequential nodes with the same path argument, the call will
        never raise NodeExistsError.

        If the parent node does not exist in ZooKeeper, a NoNodeError
        will be raised. Setting the optional `makepath` argument to
        `True` will create all missing parent nodes instead.

        An ephemeral node cannot have children. If the parent node of
        the given path is ephemeral, a NoChildrenForEphemeralsError
        will be raised.

        This operation, if successful, will trigger all the watches
        left on the node of the given path by :meth:`exists` and
        :meth:`get` API calls, and the watches left on the parent node
        by :meth:`get_children` API calls.

        The maximum allowable size of the node value is 1 MB. Values
        larger than this will cause a ZookeeperError to be raised.

        :param str path: Path of node.
        :param dict value: Initial bytes value of node.
        :param ephemeral: Boolean indicating whether node is ephemeral
                          (tied to this session).
        :param sequence: Boolean indicating whether path is suffixed
                         with a unique index.
        :returns: Real path of the new node.
        :rtype: str

        :raises:
            :exc:`~kazoo.exceptions.NodeExistsError` if the node
            already exists.

            :exc:`~kazoo.exceptions.NoNodeError` if parent nodes are
            missing.

            :exc:`~kazoo.exceptions.NoChildrenForEphemeralsError` if
            the parent node is an ephemeral node.

            :exc:`~kazoo.exceptions.ZookeeperError` if the provided
            value is too large.

            :exc:`~kazoo.exceptions.ZookeeperError` if the server
            returns a non-zero error code.

        """
        self.m_node[path] = (value, ephemeral, sequence)
        if self.m_isActive:
            try:
                # if self.m_zk.exists(path) == None:
                if self.m_zk.exists(path) is None:
                    return self.m_zk.create(path,
                                            value=bytes(json.dumps(value),
                                                        'utf-8'),
                                            ephemeral=ephemeral,
                                            makepath=True,
                                            sequence=sequence)
                else:
                    self.m_zk.set(path, bytes(json.dumps(value), 'utf-8'))
                    return path
            except NodeExistsError as ex:
                print("NodeExistsError", ex)
            except Exception as ex:
                print("Error:", ex)
                raise MyError(ex)

    def set_node(self, path, value):
        """set node info.

        if node is not exist, create path
        if node exist, Set the value of a node.

        If the version of the node being updated is newer than the
        supplied version (and the supplied version is not -1), a
        BadVersionError will be raised.

        This operation, if successful, will trigger all the watches on
        the node of the given path left by :meth:`get` API calls.

        The maximum allowable size of the value is 1 MB. Values larger
        than this will cause a ZookeeperError to be raised.

        :param str path: Path of node.
        :param bytes value: New data value.
        :returns: Updated :class:`~kazoo.protocol.states.ZnodeStat` of
                  the node.
        """
        # if path in self.m_node:
        #     try:
        #         self.m_node[path][0].update(value)
        #         if self.m_isActive:
        #             # if self.m_zk.exists(path) == None:
        #             if self.m_zk.exists(path) is None:
        #                 self.m_zk.create(path,
        #                                  value=bytes(json.dumps(self.m_node[path][0]), 'utf-8'),
        #                                  ephemeral=self.m_node[path][1],
        #                                  makepath=True,
        #                                  sequence=self.m_node[path][2])
        #             else:
        #                 self.m_zk.set(path, bytes(json.dumps(self.m_node[path][0]), 'utf-8'))
        #     except Exception as ex:
        #         print("Error:", ex)
        #         raise MyError(ex)
        try:
            if self.m_isActive:
                # if self.m_zk.exists(path) == None:
                if self.m_zk.exists(path) is None:
                    self.add_node(path, value)
                    # self.m_zk.create(path,
                    #                  value=bytes(json.dumps(self.m_node[path][0]), 'utf-8'),
                    #                  ephemeral=self.m_node[path][1],
                    #                  makepath=True,
                    #                  sequence=self.m_node[path][2])
                else:
                    tt = json.dumps(value)
                    self.m_zk.set(path, bytes(tt, encoding='utf8'))
        except Exception as ex:
            print("Error:", ex)
            raise MyError(ex)

    def update_node_time(self):
        """ update node time.

        if node is not exist, create node.
        if node exist, update the time
        """
        # if len(self.m_node) > 0 and self.m_isActive:
        if (len(self.m_node) > 0) and self.m_isActive:
            try:
                for item in self.m_node.keys():
                    if self.m_zk.exists(item):
                        self.m_zk.set(item, bytes(json.dumps(self.m_node[item][0]), 'utf-8'))
                    else:
                        self.m_zk.create(item,
                                         value=bytes(json.dumps(self.m_node[item][0]), 'utf-8'),
                                         ephemeral=self.m_node[item][1],
                                         makepath=True,
                                         sequence=self.m_node[item][2])
            except Exception as ex:
                print("Error:", ex)
                raise MyError(ex)

    def remove_node(self, path):
        """Delete a node.

        The call will succeed if such a node exists, and the given
        version matches the node's version (if the given version is -1,
        the default, it matches any node's versions).

        This operation, if successful, will trigger all the watches on
        the node of the given path left by `exists` API calls, and the
        watches on the parent node left by `get_children` API calls.

        :param path: Path of node to delete.
        """
        if path in self.m_node.keys():
            self.m_node.pop(path)

        try:
            if self.m_isActive and self.m_zk.exists(path):
                self.m_zk.delete(path, recursive=True)
        except Exception as ex:
            print("Error:", ex)
            raise MyError(ex)

    def get_node_data(self, path):
        """Get the value of a node.

        If a watch is provided, it will be left on the node with the
        given path. The watch will be triggered by a successful
        operation that sets data on the node, or deletes the node.

        :param str path: Path of node.
        :returns:
            Tuple (value, :class:`~kazoo.protocol.states.ZnodeStat`) of
            node.
        :rtype: tuple

        :raises:
            :exc:`~kazoo.exceptions.NoNodeError` if the node doesn't
            exist

            :exc:`~kazoo.exceptions.ZookeeperError` if the server
            returns a non-zero error code
        """
        try:
            if self.m_isActive:
                data, stat = self.m_zk.get(path)
                return json.loads(str(data, encoding='utf-8'))
        except kazoo.exceptions.NoNodeError as ex:
            print("Error:", ex)
        except kazoo.exceptions.ZookeeperError as ex:
            print("Error:", ex)
        except Exception as ex:
            print("Error:", ex)
            raise MyError(ex)
        return None

    def get_children(self, path):
        """Get a list of child nodes of a path.

        If a watch is provided it will be left on the node with the
        given path. The watch will be triggered by a successful
        operation that deletes the node of the given path or
        creates/deletes a child under the node.

        The list of children returned is not sorted and no guarantee is
        provided as to its natural or lexical order.

        :param path: Path of node to list.

        :returns: List of child node names, or tuple if `include_data`
                  is `True`.
        :rtype: list

        :raises:
            :exc:`~kazoo.exceptions.NoNodeError` if the node doesn't
            exist.

            :exc:`~kazoo.exceptions.ZookeeperError` if the server
            returns a non-zero error code.

        .. versionadded:: 0.5
            The `include_data` option.

        """
        return self.m_zk.get_children(path)

    def node_is_active(self, path):
        """judge path state.

        :param str path: node path
        :return: node is active
        """
        try:
            if self.m_isActive and self.m_zk.exists(path):
                data, stat = self.m_zk.get(path)
                if isinstance(stat, ZnodeStat):
                    if (time.time() - stat.mtime / 1000) < 120:
                        return True
        except Exception as ex:
            print("Error:", ex)
            raise MyError(ex)
        return False

    def add_data_watch(self, path, func):
        """Create a data watcher for a path.

        :param str path: The path to watch for data changes on.
        :param callable func: Function to call initially and every time the
                             node changes. `func` will be called with a
                             tuple, the value of the node and a
                             :class:`~kazoo.client.ZnodeStat` instance.
        :return: watch obj
        :rtype: DataWatch
        """
        watch_obj = DataWatch(client=self.m_zk, path=path, func=func)
        return watch_obj

    def add_children_watch(self, path, func):
        """Create a children watcher for a path.

        :param str path: The path to watch for data changes on.
        :param callable func: Function to call initially and every time the
                             node changes. `func` will be called with a
                             tuple, the value of the node and a
                             :class:`~kazoo.client.ZnodeStat` instance.
        :return: watch obj
        :rtype: ChildrenWatch
        """
        watch_obj = ChildrenWatch(client=self.m_zk, path=path, func=func)
        return watch_obj
