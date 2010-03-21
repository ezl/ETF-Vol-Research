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
from time import sleep

conn = sqlite3.connect("Levered_Financial_ETF_Option_and_Stock_DB.sqlite3")

symbols = ['FAS',]

pyplot.ion()
calls, puts, wt_averages, best_fit = pyplot.plot(3, 3, 'ro',
                                                 3, 3, 'bo',
                                                 3, 3, 'k*',
                                                 3, 3, 'k-')
ATM_marker = pyplot.axvline()

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
            implied_vols = {}; strikes = {}
            sql = SQL.get_strike_and_cvol_and_pvol_and_call_delta % params
            vols = execute_query_DF(conn, sql)
            call_ivs = vols('call_iv')
            put_ivs  = vols('put_iv')
            call_delta = vols('call_delta')
            strikes = vols('strike')
            strikes, call_ivs, put_ivs, call_delta = nerdy.clip_repeated_wings(
                                         strikes, call_ivs, put_ivs, call_delta)
            wt_avg_implied_vols = call_ivs * (1 - call_delta) + put_ivs * call_delta
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
            z = nerdy.moneyness(strikes, implied_forward, vol, time_to_expiration)
            # coeffs = [ 10*wing[call_put], 20*wave[call_put], 20*kurt[call_put], 16.75*skew[call_put], vol[call_put] ]
            coeffs = [wing, wave, kurt, skew, vol]
            fit_vols = scipy.polyval(coeffs, z)

#            xmin = min(strikes)
#            xmax = max(strikes)
            time.sleep(.5)
            ATM_marker.remove()
            xmin = int(implied_forward * 1/2)
            xmax = int(implied_forward * 3/2)
            ymin = min(np.hstack((call_ivs, put_ivs)))
            ymax = max(np.hstack((call_ivs, put_ivs)))
            ATM_marker = pyplot.axvline(x=implied_forward, ymin=0, ymax=1, linewidth=10, color="#B0E0E6", zorder=0)
            pyplot.axis([xmin, xmax, ymin, ymax])
            pyplot.title("F: %s, date: %s, exp: %s, points:%s" % (
                                                            implied_forward,
                                                            str(epoch2datetime(int(t_date)).date()),
                                                            str(epoch2datetime(int(expiration_date)).date()),
                                                            len(strikes) )
                        )
            graphs = [calls, puts, wt_averages, best_fit]
            y_data = [call_ivs, put_ivs, wt_avg_implied_vols, fit_vols]
            calls.set_xdata(strikes)
            for graph, y in zip(graphs, y_data):
                graph.set_xdata(strikes)
                graph.set_ydata(y)
                pyplot.draw()
            print "IF: %s".rjust(20) % implied_forward, "||",
            for prime in [vol, skew, kurt, wave, wing]:
                print prime,
            print
#
#            primes = """
#            vol : %s
#            skew: %s
#            kurt: %s
#            wave: %s
#            wing: %s""" % (vol, skew, kurt, wave,wing)
#            pyplot.text(xmin, ymin, primes)
#            pyplot.show()

