get_fit_parameter = """
            SELECT symbol1.%(fit_parameter)s AS %(fit_parameter)s1, symbol2.%(fit_parameter)s AS %(fit_parameter)s2
            FROM (SELECT * FROM VolSmile WHERE symbol='%(symbol1)s') symbol1
            JOIN (SELECT * FROM VolSmile WHERE symbol='%(symbol2)s') symbol2
            ON symbol1.t_date=symbol2.t_date
            AND symbol1.expiration_date=symbol2.expiration_date
            WHERE symbol1.t_date > %(start_date)s
            AND symbol1.t_date < %(end_date)s"""
