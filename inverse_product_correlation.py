'''
are FAS and FAZ fits related?
'''

from ipshell import ipshell
import sqlite3
from dataframe import dataframe, execute_query_DF
import nerdy
import numpy as np
from datetimetools import * 
import SQL_inverse_product_correlation as SQL
import scipy
import datetime
from matplotlib import pyplot

conn = sqlite3.connect("Levered_Financial_ETF_Option_and_Stock_DB.sqlite3")

pair = ('FAS','FAZ')
symbol1 = 'FAS'
symbol2 = 'FAZ'
fit_parameter = 'vol'
start_date = datetime.date(2009, 1, 2)
end_date = datetime.date(2009, 11, 12)

params = dict()
params['symbol1'] = symbol1
params['symbol2'] = symbol2
params['fit_parameter'] = fit_parameter
params['start_date'] = int(datetime2epoch(start_date))
params['end_date'] = int(datetime2epoch(end_date))
sql = SQL.get_fit_parameter % params
print sql
fit_parameter = execute_query_DF(conn, sql)
ipshell("")
