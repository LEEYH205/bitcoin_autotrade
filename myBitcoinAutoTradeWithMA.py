import time
import pyupbit
import datetime

import numpy as np

import slack_sdk
# slack bot 사용에 필요한 sdk import

access = "lKdFAyO6ud3ERGW60Evms82IWAhdCLtLShA4gDxq"
secret = "TPx4jDggvu8U6mE5JvxeM676zsQDsVv2ZXYxPmhe"

SLACK_TOKEN = 'xoxb-6195567078006-6228613988353-ipPa7ZGP7C5Lkxqj8GVqSrLt'
# Bot User OAuth Token을 입력합니다.
SLACK_CHANNEL = '#msgfrombot'
# 메시지를 보낼 Channel명

#-----
def Msg_bot(slack_message):         # slack bot message
    slack_token = SLACK_TOKEN       # slack bot token
    channel = SLACK_CHANNEL         # channel for sending message from slack bot
    message = slack_message         # message from slack bot
    client = slack_sdk.WebClient(token=slack_token)
    client.chat_postMessage(channel=channel, text=message)
#-----

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

def check_bestK():

    maxRor = 0
    goodK = 0.5
    chat =''
    for k in np.arange(0.1, 1.0, 0.1):
        ror = get_ror(k)
        print("%.1f %f" % (k, ror))
        chat+=("%.1f %f\n" % (k, ror))

        if(ror>maxRor):
            goodK = k
            maxRor = ror

    print("goodK : %.1f, maxRor : %f" % (goodK, maxRor))
    chat+=("goodK : %.1f, maxRor : %f" % (goodK, maxRor))
    Msg_bot(chat)
    return goodK


# 로그인
upbit = pyupbit.Upbit(access, secret)


chat=''
chat= "보유 BTC(개수) : " + str(upbit.get_balance("KRW-BTC")) + '\n' \
            + "보유 현금(원) : " + str(upbit.get_balance("KRW"))    # KRW-BTC 조회 # 보유 현금 조회

print(chat)
Msg_bot(chat)

check_newK_flag = 0
use_kVal = 0.5

use_kVal = check_bestK()
chat=''
chat=("사용할 K값 : %.1f" % (use_kVal))
Msg_bot(chat)

print("autotrade start")
Msg_bot("autotrade start")
# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")  # 09:00
        end_time = start_time + datetime.timedelta(days=1)  # 09:00 + 1일

        # 09:00:00 < 현재 < 익일 08:59:50
        if start_time < now < end_time - datetime.timedelta(seconds=10): #-10seconds : 08:59:50
            check_newK_flag = 0
            target_price = get_target_price("KRW-BTC", use_kVal)
            ma15 = get_ma15("KRW-BTC")
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price and ma15 < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)   # 수수료 제외한 전량 매수
                    chat = ''
                    chat = "$$$$ (%04d/%02d/%02d %02d:%02d:%02d) $$$$" % (nowT.year, nowT.month, nowT.day, nowT.hour, nowT.minute, nowT.second +'\n')
                    chat += "BTC buy : " +str(buy_result)
                    print(chat)
                    Msg_bot(chat)
        else:
            btc = get_balance("BTC")
            if btc > 0.00008:       # 가지고 있는 btc 가 대략 5천원 이상이면,
                upbit.sell_market_order("KRW-BTC", btc*0.9995)  # 수수료 제외한 전량 매도
                chat = ''
                chat = "$$$$ (%04d/%02d/%02d %02d:%02d:%02d) $$$$" % (nowT.year, nowT.month, nowT.day, nowT.hour, nowT.minute, nowT.second +'\n')
                chat += "BTC sell : " +str(buy_result)
                print(chat)
                Msg_bot(chat)
            if check_newK_flag == 0 :
                use_kVal = check_bestK()
                check_newK_flag = 1

        time.sleep(1)
    except Exception as e:
        print(e)
        Msg_bot(e)
        time.sleep(1)
