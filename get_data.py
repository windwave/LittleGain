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
#basics.index = basics.index.astype(int).str.zfill(9)
basics = basics.sort_index(axis=1,ascending= False)
basics.index = basics.index.astype(int)
for i in basics.index:
    tmp = str(i).zfill(6)
    print ('start to get data'+tmp)
    hist_day_data = ts.get_hist_data(tmp,retry_count=5)
    print ('get data for'+tmp+'complated')
    hist_day_data.index = hist_day_data.index.to_datetime()
    hist_day_data.to_sql(('hist_data_'+tmp),engine)
    #    hist_data_d = ts.get_hist_data(code,retry_count=5)
#    hist_data_d.to_sql(('hist_data'+str(code)),engine)
#basics.to_sql('basics',engine)

for i in basics.index:
    tmp = str(i).zfill(6)
    print ('start to get ticks data'+tmp)
    hist_day_data = ts.get_hist_data(tmp,retry_count=5)
    print ('get ticks data for'+tmp+'complated')
    hist_day_data.index = hist_day_data.index.to_datetime()
    hist_day_data.to_sql(('hist_data_ticks_'+tmp),engine)