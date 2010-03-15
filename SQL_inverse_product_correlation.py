get_fit_coeff = """
            SELECT
                symbol1.%(fit_parameter)s AS coeff1,
                symbol2.%(fit_parameter)s AS coeff2,
                symbol1.t_date AS t_date,
                symbol1.price_close AS price_close1,
                symbol2.price_close AS price_close2,
                symbol1.price_close_ini AS price_close_ini1,
                symbol2.price_close_ini AS price_close_ini2
            FROM
                    (SELECT *
                    FROM (SELECT * FROM VolSmile WHERE symbol='%(symbol1)s') vs
                    JOIN StockPrice
                        ON StockPrice.symbol=vs.symbol
                        AND StockPrice.t_date=vs.t_date
                    ) symbol1
            JOIN
                    (SELECT *
                    FROM (SELECT * FROM VolSmile WHERE symbol='%(symbol2)s') vs
                    JOIN StockPrice
                        ON StockPrice.symbol=vs.symbol
                        AND StockPrice.t_date=vs.t_date
                    ) symbol2
            ON symbol1.t_date=symbol2.t_date
            AND symbol1.expiration_date=symbol2.expiration_date
            WHERE symbol1.t_date > '%(start_date)s'
            AND symbol1.t_date < '%(end_date)s'"""
