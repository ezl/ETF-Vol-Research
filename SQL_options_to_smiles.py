get_t_dates = """
            SELECT DISTINCT t_date
            FROM OptionValue
            WHERE symbol = '%(symbol)s'"""
get_spot_closing_price = """
            SELECT price_close
            FROM StockPrice
            WHERE symbol = '%(symbol)s'
            AND t_date = '%(t_date)s'"""
get_expiration_dates = """
            SELECT DISTINCT expiration_date
            FROM OptionValue
            WHERE symbol = '%(symbol)s'
            AND t_date = '%(t_date)s'"""
get_implied_forwards = """
            SELECT
                (calls.bid - puts.ask + calls.strike) AS synthetic_bid,
                (calls.ask - puts.bid + calls.strike) AS synthetic_offer,
                calls.strike AS strike,
                calls.t_date AS t_date,
                calls.expiration_date AS expiration_date
            FROM (SELECT * FROM OptionValue WHERE symbol='%(symbol)s' AND call_put='C') AS calls
            JOIN (SELECT * FROM OptionValue WHERE symbol='%(symbol)s' AND call_put='P') AS puts
                ON calls.t_date=puts.t_date
                AND calls.expiration_date=puts.expiration_date
                AND calls.strike=puts.strike
                AND calls.call_put = 'C'
                AND puts.call_put = 'P'
                AND calls.symbol=puts.symbol
            WHERE
                calls.t_date='%(t_date)s'
                AND calls.expiration_date='%(expiration_date)s'"""
get_strike_and_vol_by_option_type = """
            SELECT strike, iv
            FROM OptionValue
            WHERE symbol='%(symbol)s'
            AND t_date='%(t_date)s'
            AND expiration_date='%(expiration_date)s'
            AND call_put ='%(call_put)s'"""
get_strike_and_cvol_and_pvol_and_call_delta = """
            SELECT call.strike AS strike, call.iv AS call_iv, put.iv AS put_iv, call.delta AS call_delta 
            FROM (SELECT * FROM OptionValue WHERE symbol='%(symbol)s' AND call_put='C') call
            JOIN (SELECT * FROM OptionValue WHERE symbol='%(symbol)s' AND call_put='P') put
            ON call.t_date='%(t_date)s'
            AND put.t_date='%(t_date)s'
            AND call.expiration_date='%(expiration_date)s'
            AND put.expiration_date='%(expiration_date)s'
            AND call.strike=put.strike"""


