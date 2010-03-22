get_t_dates = """
            SELECT DISTINCT t_date
            FROM OptionValue
            WHERE symbol = '%(symbol)s'"""
get_spot_closing_price = """
            SELECT price_close
            FROM StockPrice
            WHERE symbol = '%(symbol)s'
            AND t_date = %(t_date)s"""
get_expiration_dates_and_vols = """
            SELECT DISTINCT expiration_date, vol
            FROM VolSmile
            WHERE symbol = '%(symbol)s'
            AND t_date = %(t_date)s"""
get_strike_and_vol_by_option_type = """
            SELECT strike, iv
            FROM OptionValue
            WHERE symbol='%(symbol)s'
            AND t_date=%(t_date)s
            AND expiration_date = %(expiration_date)s
            AND call_put ='%(call_put)s'"""
get_strike_and_cvol_and_pvol_and_call_delta = """
            SELECT call.strike AS strike, call.iv AS call_iv, put.iv AS put_iv, call.delta AS call_delta 
            FROM (SELECT * FROM OptionValue WHERE symbol='%(symbol)s' AND call_put='C') call
            JOIN (SELECT * FROM OptionValue WHERE symbol='%(symbol)s' AND call_put='P') put
            ON call.t_date=%(t_date)s
            AND put.t_date=%(t_date)s
            AND call.expiration_date=%(expiration_date)s
            AND put.expiration_date=%(expiration_date)s
            AND call.strike=put.strike"""


