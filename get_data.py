# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 22:52:24 2018

@author: Test
"""
import tushare as ts
from sqlalchemy import create_engine



#get basic
basics =ts.get_stock_basics()



#run for 3 month 
#then run everyday



#write to database
#MySQL不允许在BLOB/TEXT,TINYBLOB, MED
#IUMBLOB, LONGBLOB, TINYTEXT, MEDIUMTEXT,\
# LONGTEXT,VARCHAR建索引，因为前面那些列类型都是可变长的，M
#ySQL无法保证列的唯一性，只能在BLOB/TEXT
#前n个字节上建索引，这个n最大多长呢？做个测试：
engine = create_engine('mysql://root:toor@127.0.0.1/stock?charset=utf8')

basics.to_sql('basics',engine)
