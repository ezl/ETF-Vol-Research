from ipshell import ipshell
from matplotlib import pyplot
import numpy as np
from dataframe import *
from sqlite3tools import *
import sqlite3

DBNAME = "Levered_Financial_ETF_Option_and_Stock_DB.sqlite3"
conn = sqlite3.connect(DBNAME)

SQL = """SELECT AlphaCurve.*, StockPrice.price_close AS spot, StockPrice.t_date AS stock_date
         FROM AlphaCurve JOIN StockPrice
         ON AlphaCurve.t_date=StockPrice.t_date
         AND AlphaCurve.symbol=StockPrice.symbol
         WHERE AlphaCurve.symbol='FAS'
"""

results = execute_query_DF(conn, SQL)

pivot_vol_yields = np.diff(np.log(results('pivot_vol')))
mean_vol_yields = np.diff(np.log(results('mean_vol')))
spot_yields = np.diff(np.log(results('spot')))

pyplot.plot(spot_yields, pivot_vol_yields, 'k*')
pyplot.show()

ipshell("")

