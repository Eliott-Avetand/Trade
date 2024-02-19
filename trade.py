#!/usr/bin/python3
##
# EPITECH PROJECT, 2022
# Trade
# File description:
# main file of trade
##
from decimal import DivisionByZero
import sys
from math import sqrt
from tokenize import Number

class Bot:
    def __init__(self):
        self.botState = BotState()
        self.brain = Brain([], 0)

    def run(self):
        while True:
            reading = input()
            if len(reading) == 0:
                continue
            self.parse(reading)

    def parse(self, info: str):
        tmp = info.split(" ")
        if tmp[0] == "settings":
            self.botState.update_settings(tmp[1], tmp[2])
        if tmp[0] == "update":
            if tmp[1] == "game":
                self.botState.update_game(tmp[2], tmp[3])
        if tmp[0] == "action":
            self.brain.compute(self.botState)

class Candle:
    def __init__(self, format, intel):
        tmp = intel.split(",")
        for (i, key) in enumerate(format):
            value = tmp[i]
            if key == "pair":
                self.pair = value
            if key == "date":
                self.date = int(value)
            if key == "high":
                self.high = float(value)
            if key == "low":
                self.low = float(value)
            if key == "open":
                self.open = float(value)
            if key == "close":
                self.close = float(value)
            if key == "volume":
                self.volume = float(value)

    def __repr__(self):
        return str(self.pair) + str(self.date) + str(self.close) + str(self.volume)


class Chart:
    def __init__(self):
        self.dates = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.volumes = []
        self.indicators = {}

    def add_candle(self, candle: Candle):
        self.dates.append(candle.date)
        self.opens.append(candle.open)
        self.highs.append(candle.high)
        self.lows.append(candle.low)
        self.closes.append(candle.close)
        self.volumes.append(candle.volume)


class BotState:
    def __init__(self):
        self.timeBank = 0
        self.maxTimeBank = 0
        self.timePerMove = 1
        self.candleInterval = 1
        self.candleFormat = []
        self.candlesTotal = 0
        self.candlesGiven = 0
        self.initialStack = 0
        self.transactionFee = 0.1
        self.date = 0
        self.stacks = dict()
        self.charts = dict()
        self.g = 0
        self.r = 0
        self.rSave = 0
        self.s = 0
        self.period = 7

    def update_chart(self, pair: str, new_candle_str: str):
        if not (pair in self.charts):
            self.charts[pair] = Chart()
        new_candle_obj = Candle(self.candleFormat, new_candle_str)
        self.charts[pair].add_candle(new_candle_obj)

    def update_stack(self, key: str, value: float):
        self.stacks[key] = value

    def update_settings(self, key: str, value: str):
        if key == "timebank":
            self.maxTimeBank = int(value)
            self.timeBank = int(value)
        if key == "time_per_move":
            self.timePerMove = int(value)
        if key == "candle_interval":
            self.candleInterval = int(value)
        if key == "candle_format":
            self.candleFormat = value.split(",")
        if key == "candles_total":
            self.candlesTotal = int(value)
        if key == "candles_given":
            self.candlesGiven = int(value)
        if key == "initial_stack":
            self.initialStack = int(value)
        if key == "transaction_fee_percent":
            self.transactionFee = float(value)

    def update_game(self, key: str, value: str):
        if key == "next_candles":
            new_candles = value.split(";")
            self.date = int(new_candles[0].split(",")[1])
            for candle_str in new_candles:
                candle_infos = candle_str.strip().split(",")
                self.update_chart(candle_infos[0], candle_str)
        if key == "stacks":
            new_stacks = value.split(",")
            for stack_str in new_stacks:
                stack_infos = stack_str.strip().split(":")
                self.update_stack(stack_infos[0], float(stack_infos[1]))

class Brain:
    def __init__(self, closing_prices, period):
        self.prices = closing_prices
        self.firstSMA = []
        self.secondSMA = []
        self.thirdSMA = []
        self.rsi = []
        self.averageGains = []
        self.averageLosses = []
        self.isFirstTime = True

    def SMACalc(self, days: Number):
        SMA = []

        for i in range(days):
            SMA.append(self.prices[-days + i])
        SMA = sum(SMA) / days
        return SMA

    def computeFirstRSI(self, period: Number):
        gain = []
        loss = []

        for i in range(period):
            diff = self.prices[i + 1] - self.prices[i]
            if (diff > 0):
                gain.append(diff)
                loss.append(0)
            elif (diff < 0):
                loss.append(abs(diff))
                gain.append(0)
        averageGain = sum(gain)
        averageLoss = sum(loss)
        self.averageGains.append(averageGain / period)
        self.averageLosses.append(averageLoss / period)
        rs = self.averageGains[-1] / self.averageLosses[-1] if self.averageLosses[-1] != 0 else 1
        rsi = 100 - 100 / (1 + rs)
        self.rsi.append(rsi)
        self.isFirstTime = False

    def computeFurtherRSI(self, period: Number):
        diff = self.prices[-1] - self.prices[-2]
        if (diff > 0):
            self.averageGains.append((self.averageGains[-1] * (period - 1) + diff) / period)
            self.averageLosses.append((self.averageLosses[-1] * (period - 1) + 0) / period)
        elif (diff < 0):
            self.averageGains.append((self.averageGains[-1] * (period - 1) + 0) / period)
            self.averageLosses.append((self.averageLosses[-1] * (period - 1) + abs(diff)) / period)
        rs = self.averageGains[-1] / self.averageLosses[-1] if self.averageLosses[-1] != 0 else 1
        rsi = 100 - 100 / (1 + rs)
        self.rsi.append(rsi)

    def analyzeRSI(self, affordable, btc):
        period = 7
        sellWeight = 0
        buyWeight = 0

        if (self.isFirstTime):
            self.computeFirstRSI(period)
        else:
            self.computeFurtherRSI(period)
        if (self.rsi[-1] <= 30):
            buyWeight = 30 - self.rsi[-1]
            buyWeight = buyWeight * 100 / 30
        elif (self.rsi[-1] >= 70):
            sellWeight = self.rsi[-1] - 70
            sellWeight = sellWeight * 100 / 30
        if (len(self.prices) == 338):
            print('buy USDT_BTC {}'.format(affordable))
        elif (self.prices[-1] < self.prices[-2] and self.prices[-2] > self.prices[-3] and sellWeight != 0 and btc != 0):
            print('sell USDT_BTC {}'.format(btc * sellWeight / 100))
        elif (self.prices[-1] > self.prices[-2] and self.prices[-2] < self.prices[-3] and buyWeight != 0 and affordable != 0):
            print('buy USDT_BTC {}'.format(affordable * buyWeight / 100))
        else:
            print('pass')

    def analyzeSMA(self, affordable, btc):
        if (self.firstSMA[-1] < self.secondSMA[-1] and self.firstSMA[-2] > self.secondSMA[-2]):
            print('buy USDT_BTC {}'.format(affordable))
        elif (self.firstSMA[-1] > self.secondSMA[-1] and self.firstSMA[-2] < self.secondSMA[-2]):
            print('sell USDT_BTC {}'.format(btc))
        else:
            self.analyzeRSI(affordable, btc)

    def compute(self, botState: BotState):
        self.prices = botState.charts["USDT_BTC"].closes
        dollars = botState.stacks['USDT']
        btc = botState.stacks['BTC']
        affordable = dollars / self.prices[-1]
        self.firstSMA.append(self.SMACalc(50))
        self.secondSMA.append(self.SMACalc(100))
        if (len(self.firstSMA) < 2):
            self.analyzeRSI(affordable, btc)
        else:
            self.analyzeSMA(affordable, btc)

if __name__ == "__main__":
    mybot = Bot()
    mybot.run()
