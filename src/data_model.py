'''
Data representations used within this project.
'''

from collections import defaultdict


'''
Storage for stock and options data.
'''
class TickerData:

    def __init__(self):
        # ticker : { type (option, stock) : {date : (dataframe, str)} }
        self.mp = defaultdict(lambda : defaultdict(dict))


    def add_value(self, ticker, type, date, value):
        self.mp[ticker][type][date] = value
    

    def is_ticker_exists(self, ticker):
        return ticker in self.mp


    def is_type_exists(self, ticker, type):
        return type in self.mp[ticker]
    

    def is_date_exists(self, ticker, type, date):
        return date in self.mp[ticker][type]


    def get_value(self, ticker, type, date):
        return self.mp[ticker][type][date]


    def get_last_trading_day(self, ticker, type):
        return max(self.mp[ticker][type].keys())