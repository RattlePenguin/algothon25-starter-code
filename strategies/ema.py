
import numpy as np
import pandas as pd

nInst = 50
currentPos = np.zeros(nInst)

# Store DataFrames. No need to recalculate historical data
DF = [pd.DataFrame() for _ in range(nInst)]
DFInit = False

class Trade:
    def __init__(self, active, direction, entry, stopLoss, takeProfit):
        self.active = active
        self.direction = direction
        self.entry = entry
        self.stopLoss = stopLoss
        self.takeProfit = takeProfit

trades = [Trade(False, 0, 0.0, 0.0, 0.0)] * nInst

def getMyPosition(prcSoFar):
    global currentPos
    (nins, nt) = prcSoFar.shape

    global DF
    global DFInit
    if not DFInit:
        makeDF(prcSoFar, nins)
        DFInit = True
    else:
        updateDF(prcSoFar, nins)

    for i in range(nInst):
        currentPos[i] = getMyPositionOne(i)

    return currentPos

def makeDF(prcSoFar, numInst):
    global DF
    for i in range(numInst):
        DF[i] = pd.DataFrame({'price': prcSoFar[i]})

def updateDF(prcSoFar, numInst):
    global DF
    for i in range(numInst):
        new = pd.DataFrame({'price': prcSoFar[i][-1]}, index=[0])
        DF[i] = pd.concat([DF[i], new], ignore_index=True)

def getMyPositionOne(index):
    global DF
    df = DF[index]
    df = getEMA(df, 9)
    df = getEMA(df, 21)
    df = getEMACross(df, 9, 21)
    df = getMACD(df, 5, 13, 9)

    today = df.index[-1]
    priceToday = df.loc[today, 'price']
    priceYesterday = df.loc[today - 1, 'price'] if today > 0 else priceToday

    if trades[index].active:
        if trades[index].direction == 1:
            if priceToday <= trades[index].stopLoss or priceToday >= trades[index].takeProfit:
                trades[index].active = False
                return 0
        if trades[index].direction == -1:
            if priceToday >= trades[index].stopLoss or priceToday <= trades[index].takeProfit:
                trades[index].active = False
                return 0

    df = getEMAPosition(df, 9, 21)
    crossName = "ema9ema21Cross"
    if df.loc[today, crossName] == 1:
        entry = priceToday
        stopLoss = df.loc[today, 'stopLoss']
        takeProfit = df.loc[today, 'takeProfit']
        trades[index] = Trade(True, 1, entry, stopLoss, takeProfit)
        return 1000
    elif df.loc[today, crossName] == 1:
        entry = priceToday
        stopLoss = df.loc[today, 'stopLoss']
        takeProfit = df.loc[today, 'takeProfit']
        trades[index] = Trade(True, -1, entry, stopLoss, takeProfit)
        return -1000
    return 0


def getEMA(df, span):
    """
    Gets {span}-day EMA and appends it into given DataFrame.

    Args:
        df (DataFrame): Current price and other data
        span (int): Target EMA range

    Returns:
        df (DataFrame): Data appended with the chosen EMA
    """

    emaName = "ema" + str(span)
    ema = df['price'].ewm(span=span, adjust=False).mean()
    df[emaName] = ema
    return df

def getEMACross(df, emaOne, emaTwo):
    emaOneName = "ema" + str(emaOne)
    emaTwoName = "ema" + str(emaTwo)

    df['position'] = df[emaOneName] > df[emaTwoName]
    df['positionShift'] = df['position'].shift(1)

    crossName = emaOneName + emaTwoName + "Cross"
    df[crossName] = 0
    df.loc[(df['positionShift'] == False) & (df['position'] == True), crossName] = 1
    df.loc[(df['positionShift'] == True) & (df['position'] == False), crossName] = -1
    
    df.drop(columns=['position', 'positionShift'], inplace=True)
    return df

def getEMAPosition(df, emaOne, emaTwo):
    """
    Gets the trading position using a two-EMA Crossover.
    Trading Rules:
        1. When EMA9 crosses over EMA21, buy at 500 volume. Vice versa for
            cross unders.

        2. Stop loss and take profit is the range of the previous 15 days.
    """

    if emaOne == emaTwo:
        raise ValueError("EMA values are the same.")
    elif emaOne < 1 or emaTwo < 1:
        raise ValueError("EMA values cannot be less than 1.")
    elif emaOne > emaTwo:
        emaOne, emaTwo = emaTwo, emaOne

    df['takeProfit'] = 0.00
    df['stopPrice'] = 0.00
    df['stopLoss'] = 0.00

    emaOneName = "ema" + str(emaOne)
    emaTwoName = "ema" + str(emaTwo)
    crossName = emaOneName + emaTwoName + "Cross"

    for i in range(len(df)):
        if i <= emaOne:
            # Skip empty EMA rows
            continue
        else:
            stopLoss = 0.0
            stopPrice = 0.0
            takeProfit = 0.0
            if df.loc[i, crossName] == 1:
                if df.loc[i, 'macd'] > 0:
                    stopPrice = df.loc[i, 'price']
                    allowance = df['price'].iloc[-10:].max() - df['price'].iloc[-10:].min()
                    stopLoss = stopPrice - allowance
                    takeProfit = stopPrice + allowance
            elif df.loc[i, crossName] == -1:
                if df.loc[i, 'macd'] < 0:
                    stopPrice = df.loc[i, 'price']
                    allowance = df['price'].iloc[-10:].max() - df['price'].iloc[-10:].min()
                    stopLoss = stopPrice + allowance
                    takeProfit = stopPrice - allowance

        df.loc[i, 'stopLoss'] = stopLoss
        df.loc[i, 'stopPrice'] = stopPrice
        df.loc[i, 'takeProfit'] = takeProfit

    return df

def getMACD(df, fast, slow, signal):
    df = getEMA(df, fast)
    df = getEMA(df, slow)

    emaFast = f"ema{fast}"
    emaSlow = f"ema{slow}"
    df['macdLine'] = df[emaFast] - df[emaSlow]

    df['signal'] = df['macdLine'].ewm(span=signal, adjust=False).mean()
    df['macd'] = df['macdLine'] - df['signal']

    return df