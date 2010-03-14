'''
Visually check whether the fit smiles make sense

must also compare call smiles to put smiles to see if (at a minimium) vol/skew/kurt parametrizations are close
'''

from ipshell import ipshell
import sqlite3
from dataframe import dataframe, execute_query_DF
import nerdy
import numpy as np
from datetimetools import * 
import SQL_view_smiles as SQL
import scipy
import datetime
from matplotlib import pyplot

conn = sqlite3.connect("Levered_Financial_ETF_Option_and_Stock_DB.sqlite3")

symbols = ['FAS','FAZ','SKF','UYG']
symbols = ['FAS',]

for symbol in symbols:
    params = dict()
    params['symbol'] = symbol
    sql = SQL.get_t_dates % params
    t_dates = execute_query_DF(conn, sql)
    for t_date in t_dates('t_date'):
        params['t_date'] = t_date
        sql = SQL.get_expiration_dates % params
        expiration_dates = execute_query_DF(conn, sql)
        for expiration_date in expiration_dates('expiration_date'):
            # Lets get some data
            params['expiration_date'] = expiration_date
            time_to_expiration = (float(expiration_date) - float(t_date)) / seconds_per_year
            sql = SQL.get_implied_forward % params
            implied_forward = execute_query_DF(conn, sql)('implied_forward')[0]
            sql = SQL.get_strike_and_cvol_and_pvol_and_call_delta % params
            sql = SQL.get_fit_smile % params
            fit_params = execute_query_DF(conn, sql)

            if not fit_params.numrows() == 1:
                print "Error: More than one smile matching supposedly unique criteria."
                ipshell("")
                raise Exception
            vol = fit_params('vol')[0]
            skew = fit_params('skew')[0]
            kurt = fit_params('kurt')[0]
            wave = fit_params('wave')[0]
            wing = fit_params('wing')[0]
            zmin = -2.5
            zmax = 2.5
            z = np.arange(zmin, zmax,.02)
            # coeffs = [ 10*wing[call_put], 20*wave[call_put], 20*kurt[call_put], 16.75*skew[call_put], vol[call_put] ]
            coeffs = [wing, wave, kurt, skew, vol]
            fit_vols = scipy.polyval(coeffs, z)

            # set colors for calls/puts
            pyplot.plot(z, fit_vols, '-')
            print "IF: %s".rjust(20) % implied_forward, "||",
            for prime in [vol, skew, kurt, wave, wing]:
                print prime,
            print
            pyplot.axvline(x=0, ymin=0, ymax=1, linewidth=10, color="#B0E0E6", zorder=0)

            pyplot.title("date: %s, exp: %s" % (
                         str(epoch2datetime(int(t_date)).date()),
                         str(epoch2datetime(int(expiration_date)).date())
                                               )
                        )

        xmin = zmin; xmax = zmax; ymin = 1; ymax=5
        pyplot.axis([xmin, xmax, ymin, ymax])
        pyplot.show()
        exit()

