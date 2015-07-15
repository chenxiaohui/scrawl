#!/usr/bin/python
#coding=utf-8
#Filename:driver.py
import io
import MySQLdb
import MySQLdb.cursors
from config import common_conf,haoxiana_conf

def connect(db, conf=common_conf):
    return MySQLdb.connect(conf[db]['host'], conf[db]['user'],
                           conf[db]['passwd'], conf[db]['dbname'],
                           charset = 'utf8', cursorclass=MySQLdb.cursors.DictCursor)

def to_redis():
    """"""
    pass

def to_file(item_list, conf):
    """"""
    try:
        lines = [conf['file_template']%proxy for proxy in item_list]
        with io.open(conf['filename'], 'a', encoding='utf-8') as fp:
            fp.writelines(lines)
    except Exception , e:
        raise e

def to_mysql(item_list, conf):
    """"""
    try:
        lines = [conf['value_template']%proxy for proxy in item_list]
        sql = conf['sql'] % ','.join(lines)
        mysql_execute(sql, conf)
    except Exception , e:
        raise e

#general function
def mysql_query(sql, conf = common_conf, dbname = "db", fetch_one = False):
    """"""
    results = None
    try:
        db = connect(dbname, conf)
        cursor = db.cursor()
        try:
           cursor.execute(sql)
           results = cursor.fetchone() if fetch_one else cursor.fetchall()
        except Exception, e:
           print "Error: unable to fecth data" + str(e)
           raise e
        finally:
            db.close()
    except Exception , e:
        raise e
    return results

#general function
def mysql_execute(sql, conf = common_conf, dbname = "db"):
    """"""
    affected_rows = 0
    try:
        db = connect(dbname, conf)
        cursor = db.cursor()
        try:
           affected_rows = cursor.execute(sql)
           db.commit()
        except Exception, e:
           db.rollback()
           print "Error: unable to update data" + str(e)
           raise e
        finally:
            db.close()
    except Exception , e:
        raise e

    return affected_rows

if __name__ == '__main__':
   results = mysql_query('select * from addr', haoxiana_conf)
   for result in results:
       print result['ip'], result['address'].encode('utf8')
