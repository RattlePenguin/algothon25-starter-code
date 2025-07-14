
import numpy as np
import pandas as pd

##### TODO #########################################
### IMPLEMENT 'getMyPosition' FUNCTION #############
### TO RUN, RUN 'eval.py' ##########################

nInst = 50
currentPos = np.zeros(nInst)


def getMyPosition(prcSoFar):
    global currentPos
    (nins, nt) = prcSoFar.shape
    currentPos[0] = getMyPositionOne(prcSoFar[0])
    return currentPos

def getMyPositionOne(prcSoFarOne):
    nt = prcSoFarOne.size
    df = pd.DataFrame({'price': prcSoFarOne})
    
    # Names for columns will be "SMA", "STD", "BBUpper", "BBLower", followed by
    # span e.g. "BBUpper20"

    # SMA{span} is our Middle Bollinger Band Line
    span = 20
    df = getSMA(df, span)
    df = getSTD(df, span)
    df = getBBUpper(df, span)
    df = getBBLower(df, span)

    


def getSMA(df, span):
    smaName = "sma" + str(span)
    df[smaName] = df['price'].rolling(window=span).mean()
    return df

def getSTD(df, span):
    stdName = "std" + str(span)
    df[stdName] = df['price'].rolling(window=span).std()
    return df

def getBBUpper(df, span):
    smaName = "sma" + str(span)
    stdName = "std" + str(span)
    BBUpperName = "BBUpper" + str(span)
    
    df[BBUpperName] = df[smaName] + df[stdName]
    return df

def getBBLower(df, span):
    smaName = "sma" + str(span)
    stdName = "std" + str(span)
    BBLowerName = "BBLower" + str(span)
    
    df[BBLowerName] = df[smaName] - df[stdName]
    return df
