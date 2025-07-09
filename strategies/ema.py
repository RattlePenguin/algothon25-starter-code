
import numpy as np
import pandas as pd

### IMPLEMENT 'getMyPosition' FUNCTION #############
### TO RUN, RUN 'eval.py' ##########################

nInst = 50
currentPos = np.zeros(nInst)


def getMyPosition(prcSoFar):
    global currentPos
    (nins, nt) = prcSoFar.shape
    if (nt < 2):
        return np.zeros(nins)
    lastRet = np.log(prcSoFar[:, -1] / prcSoFar[:, -2])
    lNorm = np.sqrt(lastRet.dot(lastRet))
    lastRet /= lNorm
    rpos = np.array([int(x) for x in 5000 * lastRet / prcSoFar[:, -1]])
    currentPos = np.array([int(x) for x in currentPos+rpos])
    return currentPos

def getMyPositionOne(prcSoFarOne):
    global currentPos
    nt = prcSoFarOne.size
    df = pd.DataFrame(prcSoFarOne, columns=['price'])
    ema = getEMA(df, nt)


def getEMA(prcSoFarOne, span):
    multiplier = 2 / (span + 1)
    
    sma = prcSoFarOne[:span].mean()
    for i in range(len(prcSoFarOne)):
        


In [20]: s.head()

In [21]: span = 10

In [22]: sma = s.rolling(window=span, min_periods=span).mean()[:span]

In [24]: rest = s[span:]

In [25]: pd.concat([sma, rest]).ewm(span=span, adjust=False).mean()