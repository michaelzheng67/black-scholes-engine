'''
Client workers that fetch data.
'''

import yfinance as yf
import json
import argparse
import socket
import os
import struct
import tcp_protocol
import option_utils


'''
Get past month of options data
(contract symbol, strike, last price)
'''
def fetch_options_data(ticker):
    try: 
        dat = yf.Ticker(ticker)
        for date in dat.options:
            yield date, dat.option_chain(date).calls[["contractSymbol", "strike", "lastPrice"]].to_json()
    except:
        return
    
'''
Get past month of stock data
(closing price)
'''
def fetch_stock_data(ticker):
    try:
        dat = yf.Ticker(ticker)
        df = dat.history(period='1mo')['Close']
        for i in range(len(df)):
            yield str(df.index[i].date()), df.iloc[i]
    except:
        return


'''
Get annualized volatility
'''
def fetch_stock_vol(ticker):
    try:
        dat = yf.Ticker(ticker)
        df = dat.history(period='1y')
        return option_utils.calculate_vol(df)
    except:
        return 0


'''
Higher-order function to fetch and send the correct data based on user input
'''
def send_data(c, type, ticker, func, is_df=True):

    # need to iterate through dataframe
    if is_df:
        for date, value in func(ticker):
            data = {
                "type" : type,
                "date" : date,
                "ticker" : ticker,
                "value" : value
            }

            tcp_protocol.send_data(c, data)

    else:
        data = {
            "type" : type,
            "ticker" : ticker,
            "value" : func(ticker)
        }

        tcp_protocol.send_data(c, data)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog="client")
    parser.add_argument('ticker_symbol', type=str, help='ticker symbol client fetches data for')
    parser.add_argument('--query', choices=['stock', 'option'] ,help ='fetchs either option or stock data')
    args = parser.parse_args()

    print("client starting", args.ticker_symbol)

    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.connect((os.getenv("HOST"), int(os.getenv("PORT"))))

    if args.query == 'option':
        send_data(c, "option", args.ticker_symbol, fetch_options_data)
    
    elif args.query == 'stock':
        send_data(c, "vol", args.ticker_symbol, fetch_stock_vol, False)
        send_data(c, "stock", args.ticker_symbol, fetch_stock_data)