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
fit_parameter = 'vol'
start_date = datetime.date(2009, 1, 2)
end_date = datetime.date(2009, 11, 12)
symbol1 = pair[0]
symbol2 = pair[1]

params = dict()
params['symbol1'] = symbol1
params['symbol2'] = symbol2
params['fit_parameter'] = fit_parameter
params['start_date'] = int(datetime2epoch(start_date))
params['end_date'] = int(datetime2epoch(end_date))
sql = SQL.get_fit_coeff % params
print sql
fit_coeff = execute_query_DF(conn, sql)
coeff1 = fit_coeff('coeff1')
coeff2 = fit_coeff('coeff2')
price1 = fit_coeff('price_close1')
price2 = fit_coeff('price_close2')
t_dates = fit_coeff('t_date')
price_close_ini1 = fit_coeff('price_close_ini1')
price_close_ini2 = fit_coeff('price_close_ini2')

# Linear fit

linear_fit = scipy.polyfit(coeff1, coeff2, deg=1)
xmin = min(coeff1)
xmax = max(coeff1)
fit_x = np.arange(xmin, xmax, (xmax - xmin) / 50.)
fit_y = scipy.polyval(linear_fit, fit_x)
equation = "y = %sx + %s" % tuple(linear_fit)

# Let's make some pretty pictures!
pyplot.subplot(3, 3, 1)
pyplot.plot(coeff1, coeff2, '.')
pyplot.plot(fit_x, fit_y, 'r-')
pyplot.xlabel(symbol1)
pyplot.ylabel(symbol2)
pyplot.title("%s, %s " % (fit_parameter, equation))

pyplot.subplot(3, 3, 2)
pyplot.plot(np.log(price1/price2), np.log(coeff1/coeff2), '.')
pyplot.title("%s, log(c1/c2) v log(px1/px2)" % fit_parameter)

pyplot.subplot(3, 3, 3)
pyplot.plot(t_dates, coeff1-coeff2, '.')
pyplot.twinx()
pyplot.plot(t_dates, np.log(price_close_ini1/price_close_ini2), 'r-')

pyplot.subplot(3, 3, 4)
pyplot.plot(t_dates, price1)
pyplot.title(symbol1)

pyplot.subplot(3, 3, 5)
pyplot.plot(t_dates, price2)
pyplot.title(symbol2)

pyplot.subplot(3, 3, 6)
pyplot.plot(t_dates, price_close_ini1)
pyplot.twinx()
pyplot.plot(t_dates, price_close_ini2, 'r')
pyplot.title("price_close_ini")

pyplot.subplot(3, 3, 7)
pyplot.plot(t_dates, np.log(price_close_ini1/price_close_ini2))
pyplot.title("log(%s/%s)" % (symbol1, symbol2))




pyplot.show()
ipshell("")
