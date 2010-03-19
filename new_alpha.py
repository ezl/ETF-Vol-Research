import numpy as np
from matplotlib import pyplot
import time

def alpha_theo_vol(stv, mv, alpha, t, stt):
    pivot_days = 100
    pivot_time = pivot_days / 365.
    stt = pivot_time
    vol_t = mv + (stv-mv) * ( (1 - np.exp(-alpha * t)) / (1 - np.exp(-alpha * stt)) ) * (stt / t) * np.sqrt(stt / (pivot_time))
    vol_t = mv + (stv-mv) * ( (1 - np.exp(-alpha * t)) / (1 - np.exp(-alpha * pivot_time)) ) * (stt / t)
    return vol_t

if __name__ == "__main__":
    stv = .45
    mv = .21
    alpha = 5
    st_days = 100 

    st_time = st_days / 365.
    hundred_day_time = 100 / 365.
    days = np.arange(1500)
    years = days/365.

    pyplot.ion()

    hundred_day_vol = alpha_theo_vol(stv=stv, mv=mv, alpha=alpha, t=hundred_day_time, stt=st_time)
    alpha_curve =     alpha_theo_vol(stv=stv, mv=mv, alpha=alpha, t=years, stt=st_time)
    alpha_theo_curve, left_shift, hundred_day_vol_marker, st_vol_marker = pyplot.plot(years, alpha_curve, "b-",
                                                                          years, alpha_curve, "k-",
                                                                          hundred_day_time, hundred_day_vol, "go",
                                                                          st_time, stv, "ro")
    pyplot.draw()
    for i in range(st_days):
        if i == 1:
            time.sleep(.9)
        st_time = (st_days - i) /365.
#        print st_days - i, "|", alpha_theo_vol(stv=stv, mv=mv, alpha=alpha, t=st_time, stt=st_time)
        alpha_curve = alpha_theo_vol(stv=stv, mv=mv, alpha=alpha, t=years, stt=st_time)
        hundred_day_vol = alpha_theo_vol(stv=stv, mv=mv, alpha=alpha, t=hundred_day_time, stt=st_time)
        st_vol = alpha_theo_vol(stv=stv, mv=mv, alpha=alpha, t=st_time, stt=st_time)
        alpha_theo_curve.set_ydata(alpha_curve)
#        left_shift.set_xdata(years-i/365.)
        hundred_day_vol_marker.set_ydata(hundred_day_vol)
        st_vol_marker.set_xdata(st_time)
        st_vol_marker.set_ydata(st_vol)
        pyplot.draw()
#    raw_input("[ press Enter ]")
