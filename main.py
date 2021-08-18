import websocket, json,  pprint, talib, numpy as np
import config
from binance.client import Client
from binance.enums import *



SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = "ETHUSD"    
TRADE_QUANTITY = 0.05

closes =[]
in_position = False

client = Client(config.API_KEY,config.API_SECRET,tld='us')

def order(side,quantity,symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity = quantity)
        print(order)
    except Exception as e:  
        return False

    return True

def on_open(ws):  #opening status of the socket 
    print("opened connection")

def on_close(ws): #closing status of the socket 
    print("closed connection")

def on_message(ws, message): # monitoring status of the socket for candel stick
    global closes
    global in_position
    print("received message ")
    json_message = json.loads(message)
    candel = json_message["k"]
    is_candel_closed = candel["x"] # closing ticker indiactor
    close = candel['c']  # closing price 

    if is_candel_closed: #  only the closing price  is stored 
        print("the closing price is: %s" %close )
        closes.append(float(close))
        print('closes')
        print(closes) 

        if len(closes) > RSI_PERIOD:
            np_closes = np.array(closes)
            rsi = talib.RSI(np_closes,RSI_PERIOD)
            print("all RSI calculated so far")
            print(rsi) 
            last_rsi = rsi[-1] 
            print("the last RSI value: %s" %last_rsi)

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("its overbought! so sell")
                    #binance sell logic here
                    order_succedded = order(SIDE_SELL,TRADE_QUANTITY,TRADE_SYMBOL)
                    if order_succedded:
                        in_position = False

                else:
                    print("Its over bought, we dont own any.nothing to do")

            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("IT is oversold, but you alredy own it, nothing to do")
                else:
                    print("Oversold! so buy")
                    #put binace buy logic here
                    order_succedded = order(SIDE_BUY,TRADE_QUANTITY,TRADE_SYMBOL)
                    if order_succedded:
                        in_position = True

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
