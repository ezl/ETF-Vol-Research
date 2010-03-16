import datetime
import sqlite3

import numpy as np
import scipy
from matplotlib import pyplot
from scipy.optimize import curve_fit

import nerdy
from dataframe import dataframe, execute_query_DF
import sqlite3tools
import SQL_fit_alpha_curves as SQL
from datetimetools import * 
from ipshell import ipshell

TABLENAME = "AlphaCurve"
DATABASENAME = "Levered_Financial_ETF_Option_and_Stock_DB.sqlite3"

conn = sqlite3.connect(DATABASENAME)

symbols = ['FAS','FAZ','SKF','UYG']
success = 0
skipped = 0
fail = 0
smile_count = 0

DEBUG = True
# For all expiration_dates, set debug_expiration_dates = None
debug_t_dates = [1226901600,]
debug_t_dates = None
debug_symbols = ['FAS']

# if getting data, clear the existing data first or view_smiles
# will report errors (multiple hits for unique data)
if not DEBUG is True:
    sqlite3tools.delete_sqlite_table(conn, TABLENAME)

if DEBUG is True and debug_symbols is not None:
    symbols = debug_symbols
for symbol in symbols:
    params = dict()
    params['symbol'] = symbol
    sql = SQL.get_t_dates % params
    t_dates = execute_query_DF(conn, sql)('t_date')
    if DEBUG is True and debug_t_dates is not None:
        t_dates = debug_t_dates
    for t_date in t_dates:
        print t_date
        params['t_date'] = t_date
        sql = SQL.get_expiration_dates_and_vols % params
        data = execute_query_DF(conn, sql)
        if data.numrows() < 4:
            continue
        expiration_dates = np.array([int(i) for i in data('expiration_date')])
        days = (expiration_dates - int(t_date)) / seconds_per_day

        vol = data('vol')
        def alpha(stv, mv, alpha):
            pivot = 100
            vol = mv + (stv - mv) * () * (stt/t) * np.sqrt(stt/(pivot/365))
        
        if DEBUG is True:
            pyplot.plot(days, vol, 'bo')
            pyplot.axis([0,500,.2,3.5])
            pyplot.title(epoch2datetime(int(t_date)).date())


            pyplot.show()

        if DEBUG is False:
            pass
#            columns = ('symbol', 't_date', 'expiration_date',
#                       'implied_forward', 'implied_rate',
#                       'vol', 'skew', 'kurt', 'wave', 'wing')
#            results = (symbol, t_date, expiration_date,
#                       implied_forward, implied_rate,
#                       coeffs[4], coeffs[3], coeffs[2], coeffs[1], coeffs[0])
#            sqlite3tools.insert_to_sqlite(conn, TABLENAME, columns, results)
        exit()
        pyplot.cla()
