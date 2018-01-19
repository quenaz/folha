import os
import sys
import requests
import numpy as np
from lxml import html
import datetime as dt
import monthdelta

from textblob import TextBlob
from keras.models import Sequential
from keras.layers import Dense

stocks = ['ABEV3', 'ALPA4', 'ALSC3','ALUP11','BBAS3', 'BBDC3', 'BBDC4', 'BBSD11','BBSE3', 'BEEF3', 'BOVA11','BOVV11','BRAP4', 'BRAX11', 
            'BRFS3', 'BRKM5', 'BRML3','BRPR3', 'BRSR6', 'BTOW3', 'BVMF3', 'CCRO3', 'CESP6', 'CIEL3', 'CMIG4', 'CPFE3', 'CPLE6', 'CSAN3','CSMG3',
            'CSNA3', 'CTIP3', 'CVCB3','CYRE3', 'DIVO11','DTEX3', 'ECOO11','ECOR3', 'EGIE3', 'ELET3', 'ELET6', 'ELPL4', 'EMBR3', 'ENBR3',
            'EQTL3', 'ESTC3', 'EZTC3','FIBR3', 'FIND11','FLRY3', 'GFSA3', 'GGBR4', 'GOAU4', 'GOLL4', 'GOVE11','HGTX3', 'HYPE3', 'IGTA3',
            'ISUS11','ITSA4', 'ITUB4','IVVB11','JBSS3', 'KLBN11','KROT3', 'LAME3', 'LAME4', 'LEVE3', 'LIGT3', 'LREN3', 'MATB11','MDIA3',
            'MGLU3', 'MPLU3', 'MRFG3','MRVE3', 'MULT3', 'MYPK3', 'NATU3', 'ODPV3', 'PCAR4', 'PETR3', 'PETR4', 'PIBB11','POMO4', 'PSSA3','QGEP3',
            'QUAL3', 'RADL3', 'RAPT4','RENT3', 'RUMO3', 'SANB11','SBSP3', 'SEER3', 'SMAL11','SMLE3', 'SMTO3', 'SPXI11','SULA11','SUZB5',
            'TAEE11','TIET11','TIMP3','TOTS3', 'TRPL4', 'TUPY3', 'UGPA3', 'USIM5', 'VALE3', 'VALE5', 'VIVT4', 'VLID3', 'VVAR11','WEGE3','XBOV11']

LOGIN_URL = 'https://login.folha.com.br/login?done=http://folhainvest.folha.uol.com.br/carteira&service=folhainvest'
CARTEIRA_URL = 'http://folhainvest.folha.uol.com.br/carteira?'
URL_COTACOES = 'http://folhainvest.folha.uol.com.br/cotacoes?'
ORDENS_URL = 'http://folhainvest.folha.uol.com.br/ordens?'
COMPRAR_URL = 'http://folhainvest.folha.uol.com.br/comprar?'
VENDER_URL = 'http://folhainvest.folha.uol.com.br/vender?'
CONFIRMAR_URL = 'http://folhainvest.folha.uol.com.br/confirmar?'

email, password = '', ''

def substring_after(s, delim):
    strKey = str(s.partition(delim)[2])[:44]
    return strKey

def login(email, password, session, session_id=None):
    login_data = {'email': email,
                  'password': password,
                  'signin_options': 'submit',
                  'redirect': CARTEIRA_URL
                  }

    r = session.post(LOGIN_URL, data=login_data)

    q = session.get(CARTEIRA_URL)
    
    folha_keys = str(session.cookies)

    folha_key1 = substring_after(folha_keys, '<Cookie ')
    folha_key2 = substring_after(folha_keys, ', <Cookie ')

    return folha_key1, folha_key2


def logout(session):
    q = session.get(CARTEIRA_URL + 'logout=1')
    print('LOGOUT...')


def buy_order(company, price, qty, folha_keys, pricing):
    date = str(define_date(addDays=1))

    if pricing == 'fixed':
        buy_data = {'company': company,
                    'pricing_fixed': True,
                    'value': price,
                    'quantity': qty,
                    'expiration_date': date,
                    'execute': 'submit',
                    'redirect': CONFIRMAR_URL
                    }
    elif pricing == 'market':
        buy_data = {'company': company,
                    'pricing_maket': True,
                    'quantity': qty,
                    'expiration_date': date,
                    'execute': 'submit',
                    'redirect': CONFIRMAR_URL
                    }
    else:
        return

    confirm_order = { 'confirm': 'submit' }

    session = requests.Session()
    response = session.request('GET', COMPRAR_URL + folha_keys, verify=False)

    r = session.post(COMPRAR_URL + folha_keys, data=buy_data, verify=False)
    r = session.post(CONFIRMAR_URL + folha_keys, data=confirm_order, verify=False)


def sell_order(company, price, qty, folha_keys, pricing):
    date = str(define_date(addDays=1))
    
    if pricing == 'fixed':
        sell_data = {'company': company,
                    'pricing_fixed': True,
                    'value': price,
                    'quantity': qty,
                    'expiration_date': date,
                    'execute': 'submit',
                    'redirect': CONFIRMAR_URL
                    }
    elif pricing == 'market':
        sell_data = {'company': company,
                    'pricing_market': True,
                    'quantity': qty,
                    'expiration_date': date,
                    'execute': 'submit',
                    'redirect': CONFIRMAR_URL
                    }
    else:
        return

    confirm_order = { 'confirm': 'submit' }

    session = requests.Session()
    response = session.request('GET', VENDER_URL + folha_keys, verify=False)

    r = session.post(VENDER_URL + folha_keys, data=sell_data, verify=False)
    r = session.post(CONFIRMAR_URL + folha_keys, data=confirm_order, verify=False)
    

def define_date(dateFormat="%d/%m/%Y", addDays=0, addMonth=0):
    timeNow = dt.datetime.now()

    if(addMonth!=0):
        anotherTime = timeNow - monthdelta.monthdelta(-addMonth)
    else:
        anotherTime = timeNow

    if(addDays!=0):
        anotherTime= anotherTime + dt.timedelta(days=addDays)

    return anotherTime.strftime(dateFormat)


def getHistoricalData(stockName):
    # Download our file from google finance
    url = 'http://www.google.com/finance/historical?q=BVMF%3A' + stockName + '&output=csv'
    r = requests.get(url, stream=True)

    if r.status_code != 400:
        with open(FILE_NAME, 'wb') as f:
            for chunk in r:
                f.write(chunk)
        return True

    return False


def stockPrediction(FILE_NAME, stockName, folha_keys):
    # Collect data points from csv
    dataset = []

    with open(FILE_NAME) as f:
        for n, line in enumerate(f):
            if n != 0:
                dataset.append(float(line.split(',')[4]))

    dataset = np.array(dataset)

    # Create dataset matrix (X=t and Y=t+1)
    def createDataset(dataset):
        dataX = [dataset[n + 1] for n in range(len(dataset) - 2)]
        return np.array(dataX), dataset[2:]

    trainX, trainY = createDataset(dataset)

##    # Create and fit Multilinear Perceptron model
##    model = Sequential()
##    model.add(Dense(8, input_dim=1, activation='relu'))
##    model.add(Dense(1))
##    model.compile(loss='mean_squared_error', optimizer='adam')
##    model.fit(trainX, trainY, epochs=200, batch_size=2, verbose=2)

    # Neural Net for Deep Q Learning
    # Sequential() creates the foundation of the layers.
    model = Sequential()
    # 'Dense' is the basic form of a neural network layer
    # Input Layer of state size(4) and Hidden Layer with 24 nodes
    model.add(Dense(24, input_dim=1, activation='relu'))
    # Hidden layer with 24 nodes
    model.add(Dense(24, activation='relu'))
    # Output Layer with # of actions: 2 nodes (left, right)
    model.add(Dense(1, activation='linear'))
    # Create the model based on the information above
    model.compile(loss='mse', optimizer='adam')
    model.fit(trainX, trainY, epochs=200, batch_size=2, verbose=0)

    # Our prediction for tomorrow
    prediction = model.predict(np.array([dataset[0]]))
    result = 'The price will move from %.2f to %.2f' % (
        dataset[0], prediction[0][0])

    # if price < prediction and difference in percent > 1%, BUY
    if dataset[0] < prediction[0][0] and -(((dataset[0] / prediction[0][0]) - 1) * 100) > 1.0:
        type_order = 'BUYING :::'
        print(type_order)
        buy_order(stockName, '0.0', 250, folha_keys, 'market')

    # if price > prediction and difference in percent > 1%, SELL
    elif dataset[0] > prediction[0][0] and (((dataset[0] / prediction[0][0]) - 1) * 100) > 0.5:
        type_order = 'SELLING :::'
        print(type_order)
        sell_order(stockName, '0.0', 250, folha_keys, 'market')

    # if price < prediction, UP MOVIMENT
##    elif dataset[0] < prediction[0][0] and -(((dataset[0] / prediction[0][0]) - 1) * 100) > 0.5:
##        type_order = 'UP MOVIMENT :::'
##        print(type_order)

    # if price > prediction, DOWN MOVIMENT
    elif dataset[0] > prediction[0][0] and (((dataset[0] / prediction[0][0]) - 1) * 100) > 0.5:
        type_order = 'DOWN MOVIMENT :::'
        print(type_order)
        
    # else, DO NOTHING
    else:
        type_order = 'NOTHING TO DO :::'
        print(type_order)
        
    return result, type_order


if __name__ == "__main__":
    # Where the csv file will live
    FILE_NAME = 'historicalData.csv'
    OUTPUT = 'output.txt'

    session = requests.Session()

    folha_key1, folha_key2 = login(email, password, session)
    FOLHA_KEYS = folha_key1 + '&' + folha_key2

    response = session.request('GET', CARTEIRA_URL + FOLHA_KEYS)

    fw = open(OUTPUT, 'w')

    for idx in range(len(stocks)):
        stockName = stocks[idx]
        print(stockName)

        # Check if we have the historical data for the stockName
        if not getHistoricalData(stockName):
            print('Google returned a 404, please re-run the script with a valid stock quote from IBOV')
        else:
            result, type_order = stockPrediction(FILE_NAME, stockName, FOLHA_KEYS)
            fw.write(stockName + '\n')
            fw.write(type_order + result + '\n')
            print(result)

            # We are done so we delete the csv file
            os.remove(FILE_NAME)

    fw.close()

    logout(session)
