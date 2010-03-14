import datetime
import sqlite3

import numpy as np
import scipy
from matplotlib import pyplot

import nerdy
from dataframe import dataframe, execute_query_DF
import sqlite3tools
import SQL_options_to_smiles as SQL
from datetimetools import * 
from ipshell import ipshell

TABLENAME = "VolSmile"
DATABASENAME = "Levered_Financial_ETF_Option_and_Stock_DB.sqlite3"

conn = sqlite3.connect(DATABASENAME)

symbols = ['FAS','FAZ','SKF','UYG']
success = 0
skipped = 0
fail = 0
smile_count = 0

DEBUG = False 
# For all expiration_dates, set debug_expiration_dates = None
debug_t_dates =          [1226901600,]
debug_expiration_dates = [1232172000,]
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
        print
        print symbol + ":",
        print str(epoch2datetime(int(t_date)).date()).rjust(11),
        params['t_date'] = t_date
        sql = SQL.get_spot_closing_price % params
        stock_price_data = execute_query_DF(conn, sql)('price_close')
        if not len(stock_price_data) == 1:
            msg = "More than once spot closing price for %s on %s. Bad dog."
            raise Exception, msg
        else:
            spot_closing_price = stock_price_data[0]
        sql = SQL.get_expiration_dates % params
        expiration_dates = execute_query_DF(conn, sql)('expiration_date')
        print "| # exp:", repr(len(expiration_dates)).rjust(2),
        if DEBUG is True and debug_expiration_dates is not None:
            expiration_dates = debug_expiration_dates
        for expiration_date in expiration_dates:
            smile_count += 1
            params['expiration_date'] = expiration_date
            # Get the necessary data
            sql = SQL.get_implied_forwards % params
            forward = execute_query_DF(conn, sql)
            synthetic_bids = forward('synthetic_bid')
            synthetic_offers = forward('synthetic_offer')
            days_to_expiration = (float(expiration_date) - float(t_date)) / seconds_per_day
            years_to_expiration = days_to_expiration / 365.
            print str(days_to_expiration).rjust(15),
            try:
                implied_forward = nerdy.find_implied_forward(synthetic_bids, synthetic_offers)
            except Exception, e:
                print "Exception: %s" % e
                ipshell("problem with IF")
            implied_rate = np.log(implied_forward / spot_closing_price) / years_to_expiration

            sql = SQL.get_strike_and_cvol_and_pvol_and_call_delta % params
            data = execute_query_DF(conn, sql)
            strikes = data('strike')
            call_ivs = data('call_iv')
            put_ivs = data('put_iv')
            call_delta = data('call_delta')
            strikes, call_ivs, put_ivs, call_delta = nerdy.clip_repeated_wings(
                                                     strikes, call_ivs, put_ivs, call_delta)
            delta_wt_avg_implied_vols = call_ivs * (1 - call_delta) + put_ivs * call_delta

            # print "degree: %s, len(strikes): %s, t_date: %s, expiration_date: %s" % (degree, len(strikes), t_date, expiration_date)

            # Don't fit 0 or 1 points
            if len(strikes) < 2:
                skipped += 1
                continue
            # Don't fit if strike range does not contain forward
            if not( min(strikes) < implied_forward < max(strikes) ):
                skipped += 1
                continue

            # how should we fit this smile?
            degree = min(4, len(strikes) / 2)

            # fit it
            z = nerdy.moneyness(strikes, implied_forward, 1, years_to_expiration)
            try:
                ATF_vol = nerdy.fit_smile(z, delta_wt_avg_implied_vols, degree=degree)[-1]
                z = z / ATF_vol
                coeffs = list(nerdy.fit_smile(z, delta_wt_avg_implied_vols, degree=degree))
                while not len(coeffs) >= 5:
                    coeffs.insert(0,0)
            except Exception, e:
                fail += 1
                print "Exception:", e
                ipshell("WTF")
                raise Exception, e
            else:
                if DEBUG is True:
                    print
                    print "z:"
                    print z
                    print "Spot:", spot_closing_price
                    print "IF:", implied_forward
                    print "IR:", implied_rate
                    print "ATF vol:", ATF_vol
                    print "vol: %s || skew: %s || kurt: %s || wave: %s || wing: %s" % tuple(coeffs[i] for i in range(4,-1,-1))
                    # Graph it
                    color = {'C':'r', 'P':'b'}
                    pyplot.plot(strikes, call_ivs, 'ro')
                    pyplot.plot(strikes, put_ivs, 'bo')
                    pyplot.plot(strikes, delta_wt_avg_implied_vols, 'k*')
                    fit_vols = scipy.polyval(coeffs, z)
                    pyplot.plot(strikes, fit_vols, 'k-')
                    plot_title = "days: %s, F: %s, vol: %s," % (days_to_expiration,
                                                                implied_forward, coeffs[4])
                    pyplot.title(plot_title)
                    pyplot.show()

                if DEBUG is False:
                    columns = ('symbol', 't_date', 'expiration_date',
                               'implied_forward', 'implied_rate',
                               'vol', 'skew', 'kurt', 'wave', 'wing')
                    results = (symbol, t_date, expiration_date,
                               implied_forward, implied_rate,
                               coeffs[4], coeffs[3], coeffs[2], coeffs[1], coeffs[0])
                    sqlite3tools.insert_to_sqlite(conn, TABLENAME, columns, results)
                success += 1

print
print "#smiles:", smile_count
print "success:", success
print "   fail:", fail
print "skipped:", skipped

#                    ATM_forward_vol = nerdy.polyfitw(z, implied_vols, degree=degree, w=abs(z))[-1]
#                    weights = abs(z)
#                    coeffs = nerdy.polyfitw(z, implied_vols, degree=degree, w=weights)
#                    fit_curve = scipy.polyval(coeffs, z)
