
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
    
def getRSI