import statistics
import sys
import time
import requests
import pyupbit
import numpy as np
import slack_sdk

class slack:
    def __init__(self, token, channel):
        self.token = token
        self.channel = channel

    def message(self, message):
        response = requests.post("https://slack.com/api/chat.postMessage",
                                 headers={"Authorization": "Bearer " + self.token},
                                 data={"channel": self.channel, "text": message}
                                 )

def static_vars(**kwargs):
    def decorate(func):
        for k, v in kwargs.items():
            setattr(func, k, v)
        return func

    return decorate
    
class alertV2:
    flag = 0

    def process_start(self, ticker, koreanName):
        try:
            chat = ''
            now = pyupbit.get_current_price(ticker)
            nowVolume = pyupbit.get_ohlcv(ticker, "minute15", count=1)

            # 추가: None 체크
            if nowVolume is None or nowVolume.empty:
                #print("[봇 오류] nowVolume 데이터를 가져오지 못했습니다.")
                return

            num_str = str(round(now, 2))

            df = pyupbit.get_ohlcv(ticker, "minute15", count=2)
            # 추가: None 체크
            if df is None or df.empty:
                #print("[봇 오류] df 데이터를 가져오지 못했습니다.")
                return

            max_close_index = df['close'].idxmax()
            max_close_position = df.index.get_loc(max_close_index)

            close_percent_change = ((df['close'].iloc[1] - df['close'].iloc[0]) / df['close'].iloc[0]) * 100

            chat = ''

            #print("alertV2.flag : %d" % alertV2.flag)

            if nowVolume['volume'].iloc[0] >= 20.0 :
                if close_percent_change < -0.05 and alertV2.flag != 1:
                    chat = "[비트코인-하락] 현재가격 : " + num_str + ",  " + str(
                        close_percent_change) + "%, 거래량 : " + str(
                        nowVolume['volume'].iloc[0]) + ", 현재시간 : " + time.strftime('%m-%d %H:%M')
                    slackBot.message(chat)
                    #print(chat)
                    alertV2.flag = 1

                elif close_percent_change < -0.8 and alertV2.flag != 2:
                    chat = "[비트코인-큰하락] 현재가격 : " + num_str + ",  " + str(
                        close_percent_change) + "%, 거래량 : " + str(
                        nowVolume['volume'].iloc[0]) + ", 현재시간 : " + time.strftime('%m-%d %H:%M')
                    slackBot.message(chat)
                    #print(chat)
                    alertV2.flag = 2

                elif close_percent_change < -0.9 and alertV2.flag != 3:
                    chat = "[비트코인-대피해] 현재가격 : " + num_str + ",  " + str(
                        close_percent_change) + "%, 거래량 : " + str(
                        nowVolume['volume'].iloc[0]) + ", 현재시간 : " + time.strftime('%m-%d %H:%M')
                    slackBot.message(chat)
                    #print(chat)
                    alertV2.flag = 3

                elif close_percent_change > 0.4 and alertV2.flag != 4:
                    chat = "[비트코인-상승전환] 현재가격 : " + num_str + ",  " + str(
                        close_percent_change) + "%, 거래량 : " + str(
                        nowVolume['volume'].iloc[0]) + ", 현재시간 : " + time.strftime('%m-%d %H:%M')
                    slackBot.message(chat)
                    #print(chat)
                    alertV2.flag = 4

            # 추가: 플래그 초기화
            else:
                alertV2.flag = 0

        except Exception as e:
            print(e)
            #print("[봇 오류] " + ticker)

with open("key_info.txt") as f:
    lines = f.readlines()
    acc_key = lines[0].strip()  # Access Key
    sec_key = lines[1].strip()  # Secret Key
    app_token = lines[2].strip()  # App Token
    channel = lines[3].strip()  # Slack Channel Name

slackBot = slack(app_token, channel)

slackBot.message("$$$$$ 비트코인 알람봇 시작!!")
#print("$$$$$ 비트코인 알람봇 시작!!")
while True:
    alertBot = alertV2()
    alertBot.process_start("KRW-BTC", "비트코인")
    time.sleep(0.1)
