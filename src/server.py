'''
Multi-threaded server that is the pricing arbitrage "engine".
'''

import socket
import os
import json
import struct
import time
import worker_thread
import tcp_protocol
from threading import Thread, Semaphore, Lock
from collections import defaultdict, deque
from datetime import datetime
import ui
import option_utils
import data_model


mp = data_model.TickerData() # ticker : { type (option, stock) : {date : (dataframe, str)} }
mp_vol = {} # ticker : vol
options_pricing = {} # (ticker, strike) : (market value, black-scholes value)


'''
Load in client data
'''
def client_data(conn, timer):

    try:
        data = next(tcp_protocol.accept_json_data(conn))
    except StopIteration:
        return

    # Process the data

    # if time series (stock or option)
    if data["type"] in ["option"]:

        mp.add_value(data["ticker"], data["type"], data["date"], json.loads(data["value"]))
    
    elif data["type"] in ["stock"]:

        mp.add_value(data["ticker"], data["type"], data["date"], data["value"])
    
    elif data["type"] in ["vol"]:
        
        mp_vol[data["ticker"]] = data["value"]

    
    if (mp.is_type_exists(data["ticker"], "stock") 
            and mp.is_type_exists(data["ticker"], "option")
            and data["ticker"] in mp_vol):

        find_arbitrage(data["ticker"], timer)


'''
Use Black-Scholes formula to output arbitrage opportunities based on theoretical option value
vs. current last sale price
'''
def find_arbitrage(ticker, timer):
    
    if ( not mp.is_ticker_exists("^IRX") or not mp.is_type_exists("^IRX", "stock")):
        return

    stock_price = int(mp.get_value(ticker, "stock", mp.get_last_trading_day(ticker, "stock")))
    options_df = mp.get_value(ticker, "option", mp.get_last_trading_day(ticker, "option"))

    # iterate through all rows
    for row, _ in options_df["contractSymbol"].items():
        strike_price = int(options_df["strike"][row])

        current_date_dtfmt = datetime.strptime(datetime.now().strftime("%y%m%d"), "%y%m%d")
        strike_date = datetime.strptime(
            options_df["contractSymbol"][row][len(ticker): len(ticker) + 6], "%y%m%d")

        time_difference = strike_date - current_date_dtfmt
        time_to_expiration = time_difference.days / 365 # in years

        risk_free_rate = int(
            mp.get_value(
                "^IRX", 
                "stock",
                mp.get_last_trading_day("^IRX", "stock"))) / 100
        
        vol = mp_vol[ticker]
        black_scholes = option_utils.compute_black_scholes(
            stock_price, strike_price, time_to_expiration, risk_free_rate, vol)
        
        if not black_scholes:
            return
        
        black_scholes = round(black_scholes, 2)
        options_pricing[(ticker, strike_price)] = (
                                        actual := round(float(options_df["lastPrice"][row]), 2), 
                                        black_scholes)  

        # if significant difference in actual vs theoretical pricing (greater than 20%)
        if abs(actual - black_scholes) / actual >= .2:
            print((ticker, strike_price, strike_date.strftime('%m-%d-%Y')), 
                    f"black-scholes value = {black_scholes}, actual = {actual}")


if __name__ == '__main__':
    print("server starting")
    start_time = datetime.now()
    # server socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((os.getenv("HOST"), int(os.getenv("PORT"))))
    s.listen(5)

    # spawn worker threads to receive data
    threads = set()
    try:
        while True:
            conn, _ = s.accept()
            t = worker_thread.WorkerThread(client_data, conn, start_time)
            t.start()
            threads.add(t)
    except KeyboardInterrupt:
        for t in threads:
            t.signal()