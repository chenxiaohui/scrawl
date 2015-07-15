#!/usr/bin/python
#coding=utf-8
#Filename:pool.py
import time
import threading
import io
from config import seg, common_conf

def read(conf):
    """
    read from file
    """
    try:
        proxy_list = []
        with io.open(conf['filename'], 'r', encoding='utf-8') as fp:
            lines = fp.readlines()

        for line in lines:
            proxy = line.strip('\n').split(seg)
            if proxy:
                proxy_list.append(conf['read_func'](proxy))
        return proxy_list
    except Exception , e:
        raise e

class ProxyPool(object):
    """"""
    def __init__(self, debug=False):
        super(ProxyPool,self).__init__()
        self.proxy_list = []
        self.proxy_map = {}
        self.timestmap = 0
        self.ptr = -1
        self.timespan = 10*60*1000
        self.debug = debug
        self.lock = threading.Lock()
        self.valid_cnt = 0

    def rebuild_hashmap(self):
        """"""
        self.proxy_map.clear()
        for proxy in self.proxy_list:
            self.proxy_map[proxy['proxy']] = proxy

    def reload(self):
        """"""
        if self.debug:
            self.mock()
        else:
            self.proxy_list = read(common_conf)
            self.proxy_list.append({'proxy':u'direct','valid':10})

        self.rebuild_hashmap()
        self.valid_cnt = len(self.proxy_list)
        self.timestmap=int(round(time.time() * 1000))
        self.ptr=-1

    def mock(self):
        """"""
        self.proxy_list = [
            {'proxy':"aa", 'valid':1},
            {'proxy':"ba", 'valid':1},
            {'proxy':"ab", 'valid':1},
            {'proxy':"bb", 'valid':1}
        ]

    def get_proxy(self):
        """
        select a proxy from global_proxy_pool using some strategy
        """
        timestmap = int(round(time.time() * 1000))
        self.lock.acquire()
        if timestmap - self.timestmap > self.timespan:
            self.reload()
        self.ptr = (self.ptr + 1) % len(self.proxy_list)
        while self.has_valid_proxy() and self.proxy_list[self.ptr]['valid'] <= 0:
            self.ptr = (self.ptr + 1) % len(self.proxy_list)
        proxy = self.proxy_list[self.ptr] if self.has_valid_proxy() else {'proxy':u'direct','valid':10}
        self.lock.release()
        return proxy

    def set_proxy_invalid(self, proxy_ip):
        """"""
        self.lock.acquire()
        proxy = self.proxy_map[proxy_ip['proxy']]
        if proxy and proxy['valid'] > 0:
            proxy['valid'] -= 1
            if (proxy['valid'] <= 0):
                self.valid_cnt -= 1
        else:
            print "warning:" + str(proxy)
        self.lock.release()

    def has_valid_proxy(self):
        """"""
        return self.valid_cnt > 0

    def get_proxy_cnt(self):
        """"""
        return self.valid_cnt

    def dump(self):
        """"""
        for proxy in self.proxy_list:
            print proxy


import unittest

class TestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test(self):
        pool = ProxyPool(True)
        proxy= pool.get_proxy()
        pool.set_proxy_invalid(proxy)

        proxy= pool.get_proxy()
        pool.set_proxy_invalid(proxy)

        proxy= pool.get_proxy()
        pool.set_proxy_invalid(proxy)

        self.assertEqual(pool.get_proxy(), {'proxy':"bb", 'valid':1})
        self.assertEqual(pool.get_proxy(), {'proxy':"bb", 'valid':1})
        self.assertEqual(pool.get_proxy(), {'proxy':"bb", 'valid':1})

if __name__ == "__main__":
    unittest.main()


#if __name__ == '__main__':

    #pool = ProxyPool()
    #print pool.get_proxy()
    #print pool.get_proxy()
    #print 

    #pool.set_proxy_invalid(u"direct")
    #print pool.get_proxy()
    #print pool.get_proxy()
    #print pool.get_proxy()
    #print pool.get_proxy()

    #pool.dump()

