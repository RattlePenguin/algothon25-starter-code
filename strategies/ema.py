
import numpy as np
import pandas as pd

### IMPLEMENT 'getMyPosition' FUNCTION #############
### TO RUN, RUN 'eval.py' ##########################

nInst = 50
currentPos = np.zeros(nInst)

# TODO: Store DataFrame so no need to recalculate historical data
# df = None

# Global trade state for one instrument
state = {
    'active': False,
    'direction': 0, # +1 long -1 short
    'stoploss': 0.0,
    'takeProfit': 0.0
}

def getMyPosition(prcSoFar):
    global currentPos
    (nins, nt) = prcSoFar.shape

    currentPos[0] = getMyPositionOne(prcSoFar[0])

    return currentPos

def getMyPositionOne(prcSoFarOne):
    # global df
    global state
    nt = prcSoFarOne.size

    df = pd.DataFrame({'price': prcSoFarOne})
    df = getEMA(df, 50)
    df = getEMA(df, 200)
    df = getEMACross(df, 50, 200)

    today = df.index[-1]
    priceToday = df.loc[today, 'price']
    priceYesterday = df.loc[today - 1, 'price'] if today > 0 else priceToday

    # Exit strategy
    if state['active']:
        if state['direction'] == 1:
            if priceToday <= state['stopLoss']:
                print(f"Exiting LONG at day {today}: price={priceToday:.2f} — Hit STOP LOSS at {state['stopLoss']:.2f}")
                state['active'] = False
                return 0
            elif priceToday >= state['takeProfit']:
                print(f"Exiting LONG at day {today}: price={priceToday:.2f} — Hit TAKE PROFIT at {state['takeProfit']:.2f}")
                state['active'] = False
                return 0
            else:
                return 1000  # maintain long position

        elif state['direction'] == -1:
            if priceToday >= state['stopLoss']:
                print(f"Exiting SHORT at day {today}: price={priceToday:.2f} — Hit STOP LOSS at {state['stopLoss']:.2f}")
                state['active'] = False
                return 0
            elif priceToday <= state['takeProfit']:
                print(f"Exiting SHORT at day {today}: price={priceToday:.2f} — Hit TAKE PROFIT at {state['takeProfit']:.2f}")
                state['active'] = False
                return 0
            else:
                return -1000  # maintain short position


    df = getEMAPosition(df, 50, 200)
    crossName = "ema50ema200Cross"
    if df.loc[today, crossName]:
        if priceToday > priceYesterday:  # bullish candle
            entry = priceToday
            stop = df.loc[today, 'stopLoss']
            tp = df.loc[today, 'takeProfit']
            state = {
                'active': True,
                'direction': 1,
                'stopLoss': stop,
                'takeProfit': tp
            }
            print(f"Entering LONG at day {today}: price={entry:.2f}, stop={stop:.2f}, tp={tp:.2f}")
            return 1000

        elif priceToday < priceYesterday:  # bearish candle
            entry = priceToday
            stop = df.loc[today, 'stopLoss']
            tp = df.loc[today, 'takeProfit']
            state = {
                'active': True,
                'direction': -1,
                'stopLoss': stop,
                'takeProfit': tp
            }
            print(f"Entering SHORT at day {today}: price={entry:.2f}, stop={stop:.2f}, tp={tp:.2f}")
            return -1000

    # crossName = 'ema50ema200Cross'
    # if df[crossName].any():
    #     print(f"Crossover occurred at indices: {df.index[df[crossName]].tolist()}")
    # else:
    #     print("No crossover occurred.")

    # trades = df[df['stopPrice'] > 0]

    # if not trades.empty:
    #     print(f"{len(trades)} trade(s) were generated. Indices:")
    #     print(trades[['price', 'stopPrice', 'stopLoss', 'takeProfit']])
    # else:
    #     print("No trade entries generated.")
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
    df[crossName] = (df['position'] != df['positionShift']).fillna(False)
    
    df.drop(columns=['position', 'positionShift'], inplace=True)
    return df

def getEMAPosition(df, emaOne, emaTwo):
    """
    Gets the trading position using a two-EMA Crossover.
    Trading Rules:
        1. The entry price (stopPrice) is the price of
            the previous completed candle

        2. distance is the absolute difference between the corresponding highest
            EMA and the stopPrice

        3. The takeProfit and stopLoss are distance added or subtracted from
            stopPrice correspondingly for a BUY or SELL
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
            if df.loc[i, crossName]:
                # GREEN candle
                if df.loc[i, 'price'] > df.loc[i - 1, 'price']:
                    stopPrice = df.loc[i, 'price']
                    distance = abs(df.loc[i, emaTwoName] - stopPrice)
                    stopLoss = stopPrice - distance
                    takeProfit = stopPrice + distance
                # RED candle
                else:
                    stopPrice = df.loc[i, 'price']
                    distance = abs(df.loc[i, emaTwoName] - stopPrice)
                    stopLoss = stopPrice + distance
                    takeProfit = stopPrice - distance

                df.loc[i, 'stopLoss'] = stopLoss
                df.loc[i, 'stopPrice'] = stopPrice
                df.loc[i, 'takeProfit'] = takeProfit

    return df