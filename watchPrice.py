import time
import pyupbit
import datetime

import numpy as np

access = "lKdFAyO6ud3ERGW60Evms82IWAhdCLtLShA4gDxq"
secret = "TPx4jDggvu8U6mE5JvxeM676zsQDsVv2ZXYxPmhe"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)

chat=''
chat= "보유 BTC(개수) : " + str(upbit.get_balance("KRW-BTC")) + '\n' \
            + "보유 현금(원) : " + str(upbit.get_balance("KRW"))    # KRW-BTC 조회 # 보유 현금 조회

print(chat)


def get_ror(k):
    df = pyupbit.get_ohlcv("KRW-BTC", count=2)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    fee = 0.0032
    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'] - fee,
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror

def check_bestK():

    maxRor = 0
    goodK = 0.5
    for k in np.arange(0.1, 1.0, 0.1):
        ror = get_ror(k)
        print("%.1f %f" % (k, ror))

        if(ror>maxRor):
            goodK = k
            maxRor = ror

    print("goodK값 : %.1f, maxROR(수익률) : %f" % (goodK, maxRor))
    return goodK

use_kVal = 0.5
use_kVal = check_bestK()
print("사용할 K값 : %.1f" % (use_kVal))


now = datetime.datetime.now()
start_time = get_start_time("KRW-BTC")  # 09:00
end_time = start_time + datetime.timedelta(days=1)  # 09:00 + 1일

# 09:00:00 < 현재 < 익일 08:59:50
if start_time < now < end_time - datetime.timedelta(seconds=10): #-10seconds : 08:59:50
    target_price = get_target_price("KRW-BTC", use_kVal)
    ma15 = get_ma15("KRW-BTC")
    current_price = get_current_price("KRW-BTC")
    
    print("target_price : " + str(target_price))
    print("ma15 : " + str(ma15))
    print("current_price : " + str(current_price))
    if target_price < current_price:
        print("now-1!")
    if ma15 < current_price:
        print("now-2!")
        