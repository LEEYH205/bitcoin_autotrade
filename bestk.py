import pyupbit
import numpy as np


def get_ror(k):
    df = pyupbit.get_ohlcv("KRW-BTC", count=7)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    fee = 0.0032
    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'] - fee,
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror

maxRor = 0
goodK = 0.5

for k in np.arange(0.1, 1.0, 0.1):
    ror = get_ror(k)
    print("%.1f %f" % (k, ror))
    if(ror>maxRor):
        goodK = k
        maxRor = ror

print("goodK : %.1f, maxRor : %f" % (goodK, maxRor))