#!/usr/bin/python
#coding=utf-8
#Filename:config.py
import re
seg=u"\t\t"
bar_pattern = re.compile(r'width: (\d+)%')
ip_pattern = re.compile(r'IP地址: ([\d\.]*)</b>')

def clean(text):
    """"""
    return re.sub('[\t\ \n\r]','',text)

common_conf = {
    'timeout':10,
    'buf_size':20,
    'consumer_size':10,
    'producer_size':1,
    'read_func':lambda proxy: {'proxy':proxy[0].strip(), 'valid':3},
    'hdr' : {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'
    },
    'filename':'/usr/local/nginx/html/proxy-list.txt',
    'file_template':u"%(proxy)s\n",
}

haoxiana_conf = dict(common_conf, **{
    'url' : 'http://ip.haoxiana.com/%s.html',
    'xpath': '//table/tr[position() mod 2 = 1]',
    'parse_func':lambda item : {
        'ip':item[1].text_content(),
        'location':clean(item[3].text_content()),
    },
    "db" : {'host':"localhost",'user':"root",'passwd':"root",'dbname':"ipaddr"},
    'file_template':u"%(ip)s" + seg + u"%(location)s\n",
    'value_template':u"('%(ip)s', '%(location)s')",
    'sql':u"replace into addr values %s",
    'filename':'output.txt'
})

mi_app_conf = dict(common_conf, **{
    'url' : 'http://app.mi.com/detail/%s/',
    'parse_func':lambda dom : {
        'author':dom.xpath('//div[@class="intro-titles"]')[0].getchildren()[0].text,
        'name':dom.xpath('//div[@class="intro-titles"]')[0].getchildren()[1].text,
        'category':dom.xpath('//div[@class="intro-titles"]')[0].getchildren()[2].text_content(),
        'desc':dom.xpath('//div[@class="app-text"]/p')[0].text
    },
    "db" : {'host':"localhost",'user':"root",'passwd':"root",'dbname':"miapp"},
    'file_template':u"%(name)s\n%(url)s\n%(author)s\n%(category)s\n%(desc)s\n\n",
    'value_template':u"('%(name)s', '%(desc)s', '%(author)s', '%(category)s')",
    'sql':u"replace into app values %s",
    'filename':'output.txt'
})

conf = mi_app_conf
