import datetime
import sqlite3

import numpy as np
import scipy
from matplotlib import pyplot

import nerdy
from dataframe import dataframe, execute_query_DF
import sqlite3tools
import SQL_fit_alpha_curves as SQL
from datetimetools import * 
from ipshell import ipshell
from time import sleep

TABLENAME = "AlphaCurve"
DATABASENAME = "Levered_Financial_ETF_Option_and_Stock_DB.sqlite3"

conn = sqlite3.connect(DATABASENAME)

symbols = ['FAS','FAZ','SKF','UYG']
success = 0
skipped = 0
fail = 0
smile_count = 0

DEBUG = False
GRAPH = True
# For all expiration_dates, set debug_expiration_dates = None
debug_t_dates = [1226901600,]
debug_t_dates = None
debug_symbols = ['FAS']

# if getting data, clear the existing data first or view_smiles
# will report errors (multiple hits for unique data)
if not DEBUG is True:
    sqlite3tools.delete_sqlite_table(conn, TABLENAME)

if GRAPH is True:
    pyplot.ion()
    term_vols, alpha_curve = pyplot.plot(0, 0, 'bo',
                                         0, 0, 'k-')
    xmin = 0
    xmax = 500
    ymin = .2
    ymax = 3.5
    pyplot.axis([xmin, xmax, ymin, ymax])

    alpha_days = np.arange(0, 500, 2)

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
        times_to_expiration = days / 365.

        vol = data('vol')

        from alpha import alpha_theo_vol
        coeffs = nerdy.wls_fit(alpha_theo_vol,[1,.7,5], times_to_expiration, vol, lb=[.3,.2,1],ub=[5,3,10])
        alpha_vols = alpha_theo_vol(coeffs, alpha_days/365.)

        if GRAPH is True:
            sleep(.1)
            pyplot.title(epoch2datetime(int(t_date)).date())
            term_vols.set_xdata(days)
            term_vols.set_ydata(vol)
            alpha_curve.set_xdata(alpha_days)
            alpha_curve.set_ydata(alpha_vols)
            pyplot.draw()

        if DEBUG is False:
            pass
            columns = ('symbol', 't_date',
                       'pivot_vol', 'mean_vol', 'alpha', 'expirations')
            results = (symbol, t_date,
                       coeffs[0], coeffs[1], coeffs[2], len(expiration_dates))
            sqlite3tools.insert_to_sqlite(conn, TABLENAME, columns, results)
