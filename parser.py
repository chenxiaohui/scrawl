#!/usr/bin/python
#coding=utf-8
#Filename:test.py
from multiprocessing import Queue
#from urllib2 import urlopen, Request
import urllib2
import sys
from config import *
from driver import to_mysql, to_file
import threading
from pool import ProxyPool
import lxml.html.soupparser as soupparser

queue = Queue(conf['buf_size'])
fail = Queue()
proxy = ProxyPool()
total = 0
finish = 0
lock = threading.Lock()

class Producer(threading.Thread):
    """"""
    def __init__(self, filename):
        super(Producer, self).__init__()
        self.filename = filename

    def run(self):
        try:
            global total
            total = len(open(self.filename, 'r').readlines())
            with open(self.filename, 'r') as fp:
                url = fp.readline().strip('\n')
                while url:
                    queue.put({"url":conf['url'] % url,"proxy":proxy.get_proxy()})
                    url = fp.readline().strip('\n')
        except Exception , e:
            print str(e)

        for i in range(0, conf['consumer_size']):
            queue.put(".quit")

class Consumer(threading.Thread):
    """"""
    def __init__(self):
        super(Consumer,self).__init__()

    def run(self):
        while True:
            task = queue.get()
            if isinstance(task, str) and task=='.quit':
                break
            if not parse(task):
                proxy.set_proxy_invalid(task['proxy'])
                fail.put(task)

        #print "deal with fails"
        while True:
            try:
                task = fail.get(True, conf['timeout'] + 1)
                task['proxy'] = proxy.get_proxy()
                if not parse(task):
                    proxy.set_proxy_invalid(task['proxy'])
                    fail.put(task)
            except Exception:
                break

def parse(task):
    """
    parse html and get proxy list
    """
    try:
        results = []
        proxy_ip = task['proxy']['proxy']
        if proxy_ip == 'direct':
            opener = urllib2.build_opener()
        else:
            proxy_handler = urllib2.ProxyHandler({"http" : 'http://' + proxy_ip})
            opener = urllib2.build_opener(proxy_handler)

        opener.addheaders = conf['hdr'].items()
        html = opener.open(task['url'], timeout=conf['timeout'])
        dom = soupparser.fromstring(html)

        try:
            if 'xpath' in conf.keys():
                items = dom.xpath(conf['xpath'])
                for item in items:
                    result = conf['parse_func'](item.getchildren())
                    result['url'] = task['url']
                    results.append(result)
            elif 'parse_func' in conf.keys():
                result = conf['parse_func'](dom)
                result['url'] = task['url']
                results.append(result)

            to_mysql(results, conf)
            to_file(results, conf)
        except Exception , e:
            print str(e),

        global finish, lock
        lock.acquire()
        finish += 1
        lock.release()
        print task["url"] +  " done. finished %d/%d. proxy %s" %(finish, total, proxy_ip)
        return True
    except Exception,e:
        #remove this proxy
        print proxy_ip + " invalid. live proxy: " + str(proxy.get_proxy_cnt())
        return False

def help():
    """"""
    print "./checker.py <filename>"

if __name__ == '__main__':
    filename = None
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    else:
        help()
        exit()

    consumers = [Consumer() for i in xrange(0, conf['consumer_size'])]
    producers = [Producer(filename) for i in xrange(0, conf['producer_size'])]
    [producer.start() for producer in producers]
    [consumer.start() for consumer in consumers]
    [producer.join() for producer in producers]
    [consumer.join() for consumer in consumers]
    proxy.dump()
