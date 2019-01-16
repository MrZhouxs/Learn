"""cache process package.

all cache process class.

Cache is implement cache option func.
"""
import memcache


class Cache(object):
    """cache option class.

    所属单元: 数据汇聚缓存单元

    support cache option func, common func define.
    """

    def __init__(self, conn_info):
        """init func.

        :param conn_info: cache server connect info.
        """
        self.conn_info = conn_info
        self.__mc = self.__connect_mc(self.conn_info)

    def __connect_mc(self, conn_info):
        """connect cache func.

        client that connect to cache server implement.

        :param conn_info: cache connect auth info and weight
        :return: cache connection instance
        """
        mc_conn = memcache.Client(conn_info)
        return mc_conn

    def get_stat(self, stat_args=None):
        """ get memcache server basic connect state.

        :param stat_args: Additional arguments to pass to the memcache
            "stats" command.

        :return: A list of tuples ( server_identifier,
            stats_dictionary ).  The dictionary contains a number of
            name/value pairs specifying the name of the status field
            and the string value associated with it.  The values are
            not converted from strings.
        """
        return self.__mc.get_stats(stat_args)

    def set(self, key, val, time=0, min_compress_len=0, no_reply=False):
        """set key-value in cache.

        put one key-value in cache.

        :param key: key
        :param val : the value bind key
        :param time: Tells memcached the time which this value should
                    expire, either as a delta number of seconds, or an absolute
                    unix time-since-the-epoch value.

        :param min_compress_len: The threshold length to kick in
                                auto-compression of the value using the compressor
                                routine.

        :param no_reply: optional parameter instructs the server to not
                        send the reply.
        :return: Nonzero on success.
        """
        return self.__mc.set(key, val, time=time,
                             min_compress_len=min_compress_len, noreply=no_reply)

    def set_multi(self, mapping, time=0, key_prefix='', min_compress_len=0, no_reply=False):
        """set multi key-values in cache.

        Sets multiple keys in the cache doing just one query.

        :param mapping: A dict of key/value pairs to set.

        :param time: Tells memcached the time which this value should
            expire, either as a delta number of seconds, or an
            absolute unix time-since-the-epoch value.

        :param key_prefix: Optional string to prepend to each key when
            sending to cache. Allows you to efficiently stuff these
            keys into a pseudo-namespace in cache:
        :param min_compress_len: The threshold length to kick in
                    auto-compression of the value using the compressor
                    routine.
        :param no_reply: optional parameter instructs the server to not
                    send the reply.
        :return: Nonzero on success.
        """
        return self.__mc.set_multi(mapping, time=time, key_prefix=key_prefix,
                                   min_compress_len=min_compress_len,
                                   noreply=no_reply)

    def gets(self, key):
        """get key value.

        Retrieves a key from the cache. Used in conjunction with 'cas'.

        :param key: use the key get value safety
        :return: The value or None.
        """
        return self.__mc.gets(key)

    def get(self, key):
        """Retrieves a key from the cache.

        :param key: get value from the key
        :return: The value or None.
        """
        result = self.__mc.get(key)
        return result

    def get_multi(self, keys, key_prefix=''):
        """get multi keys values.

        get multiple value as a key-value dict from a keys list

        :param keys: An array of keys.

        :param key_prefix: A string to prefix each key when we
            communicate with cache.  Facilitates pseudo-namespaces
            within cache. Returned dictionary keys will not have this
            prefix.

        :return: A dictionary of key/value pairs that were
            available. If key_prefix was provided, the keys in the returned
            dictionary will not have it present.
        """
        result = self.__mc.get_multi(keys, key_prefix=key_prefix)
        return result

    def delete(self, key, time=None, key_prefix='', no_reply=False):
        """delete key in cache.

        Deletes a key or a keys list from the cache.

        :param key: delete value from the key
        :param time: number of seconds any subsequent set / update commands
                    should fail. Defaults to None for no delay.
        :param key_prefix: A string to prefix each key when we
                    communicate with cache.  Facilitates pseudo-namespaces
                    within cache. Returned dictionary keys will not have this
                    prefix.
        :param no_reply: optional parameter instructs the server to not send the
                    reply.
        :return: Boolean
        """
        if isinstance(key, list):
            result = self.__mc.delete_multi(key,
                                            time=time,
                                            key_prefix=key_prefix,
                                            noreply=no_reply)
        else:
            result = self.__mc.delete(key, time=time, noreply=no_reply)
        state = True if result == 1 else False
        return state

    def append(self, key, val, time=0, min_compress_len=0, no_reply=False, head=True):
        """append key-value in cache.

        Append  or pre append the value to the end of the existing key's value.

        Only stores in cache if key already exists.

        :param key: key
        :param val: the value you want prepend or append

        :param time: Tells memcached the time which this value should
                expire, either as a delta number of seconds, or an
                absolute unix time-since-the-epoch value.

        :param min_compress_len: The threshold length to kick in
                auto-compression of the value using the compressor
                routine. If the value being cached is a string, then the
                length of the string is measured, else if the value is an
                object, then the length of the pickle result is measured.

        :param no_reply: if a reply from this func default no
        :param head: prepend or append default prepend
        :return:  Nonzero on success.
        """
        if head:
            ret = self.__mc.prepend(key,
                                    val,
                                    time=time,
                                    min_compress_len=min_compress_len,
                                    noreply=no_reply)
        else:
            ret = self.__mc.append(key,
                                   val,
                                   time=time,
                                   min_compress_len=min_compress_len,
                                   noreply=no_reply)
        return ret

    def cas(self, key, val, time=0, min_compress_len=0, no_reply=False):
        """Check and set (CAS).

        Sets a key to a given value in the memcache if it hasn't been
        altered since last fetched.

        :param key: key
        :param val : the value bind key

        :param time: Tells memcached the time which this value should
            expire, either as a delta number of seconds, or an absolute
            unix time-since-the-epoch value. See the memcached protocol
            docs section "Storage Commands" for more info on <exptime>. We
            default to 0 == cache forever.

        :param min_compress_len: The threshold length to kick in
            auto-compression of the value using the compressor
            routine. If the value being cached is a string, then the
            length of the string is measured, else if the value is an
            object, then the length of the pickle result is measured. If
            the resulting attempt at compression yields a larger string
            than the input, then it is discarded. For backwards
            compatibility, this parameter defaults to 0, indicating don't
            ever try to compress.

        :param no_reply: optional parameter instructs the server to not
            send the reply.
        :return: Nonzero on success.
        """
        return self.__mc.cas(key,
                             val,
                             time=time,
                             min_compress_len=min_compress_len,
                             noreply=no_reply)

    def incr(self, key, delta=1, no_reply=False):
        """increase by itself with the value delta.

        :param key: key
        :param delta: Integer amount to increment by (should be zero
                    or greater).

        :param no_reply: optional parameter instructs the server to not send the
                        reply.

        :return: New value after incrementing, no None for noreply or error.

        """
        return self.__mc.incr(key, delta=delta, noreply=no_reply)

    def decr(self, key, delta=1, no_reply=False):
        """decrease by itself with the value delta.

        :param key: key
        :param delta: Integer amount to decrement by (should be zero
                    or greater).

        :param no_reply: optional parameter instructs the server to not send the
                        reply.

        :return: New value after decrementing,  or None for noreply or error.
        """
        return self.__mc.decr(key, delta=delta, noreply=no_reply)
