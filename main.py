import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

from utility.current_allocation import current_allocation
from utility.liquidate import liquidate


class trade:

    def __init__(self, ticker, quantity_purchased, date_purchased, asset_type, date_sold=None, leverage=1, short=False,
                 market='NYSE'):

        self.ticker = ticker
        self.quantity_purchased = quantity_purchased
        self.date_purchased = datetime.strptime(date_purchased, '%Y-%m-%d')
        self.asset_type = asset_type
        self.date_sold = date_sold
        self.leverage = leverage
        self.short = short

        # If this is an equity we must define what market it is traded on. Usually NYSE.
        if asset_type == 'equity':
            self.market = market

            if self.date_sold is not None:
                if datetime.strptime(self.date_sold, '%Y-%m-%d').weekday() > 5:
                    raise Exception('Invalid purchase date. Equities markets are closed on weekends.')

        # Sanity checks
        if date_sold is not None:

            if self.date_purchased > datetime.strptime(self.date_sold, '%Y-%m-%d'):
                raise Exception('Date sold is before date purchased.')

        if quantity_purchased <= 0:
            raise Exception('Quantity purchased is negative or 0.')

        if leverage <= 0:
            raise Exception('Leverage is negative or 0.')

        if not isinstance(short, bool):
            raise Exception('Short should be a boolean value.')

    def __repr__(self):

        return self.ticker

    def pnl(self):

        date_sold = self.date_sold

        if date_sold is None:
            date_sold = datetime.today()

        asset = yf.Ticker(self.ticker)

        price_history = asset.history(self.ticker, start=self.date_purchased, end=date_sold)['Close']
        price_change = (price_history[0] - price_history[-1])

        # Is short * quantity_purchased * price change * leverage = profit/loss.
        return np.sign((not self.short) - 0.5) * self.quantity_purchased * price_change * self.leverage

    def value(self):



    def graph(self):
        # TODO: Graph leverage properly.

        date_sold = self.date_sold

        if date_sold is None:
            date_sold = datetime.today()

        asset = yf.Ticker(self.ticker)
        price_history = self.quantity_purchased * asset.history(self.ticker, start=self.date_purchased, end=date_sold)[
            'Close']
        plt.plot(price_history)
        plt.show()


class portfolio:

    def __init__(self, *assets):
        self.asset_list = [*assets]

    def add_trade(self, asset):
        self.asset_list.append(asset)

    def pnl(self):
        total_value = 0

        for asset in self.asset_list:
            total_value += asset.pnl()

        return total_value


def graph_portfolio():
    # Defined and fixed for our use case.
    portfolio_cash = 100000
    start_date = '2022-02-24'

    # Import the spreadsheet.
    df = pd.read_csv('Alpha Fund - Sheet1.csv')

    # Perform calculations.
    portfolio_cash, asset_dictionary = current_allocation(portfolio_cash, df)
    portfolio_value, assets_over_time = liquidate(start_date, asset_dictionary)

    plt.plot(portfolio_cash + assets_over_time)
    plt.xticks(rotation=45)
    plt.subplots_adjust(bottom=0.21)
    plt.subplots_adjust(left=0.15)
    plt.xlabel('Date')
    plt.ylabel('Price (USD $)')
    plt.title('Alpha Fund Portfolio')
    plt.show()


if __name__ == '__main__':

    cash = 50000

    asset1 = trade(ticker='GSK.L', quantity_purchased=6, date_purchased='2022-02-24', asset_type='equity', leverage=1,
                   short=False)

    asset2 = trade(ticker='UPST', quantity_purchased=77, date_purchased='2022-02-24', asset_type='equity', leverage=1,
                   short=False)

    asset3 = trade(ticker='HNT-USD', quantity_purchased=447, date_purchased='2022-02-24', asset_type='equity', leverage=1,
                   short=False)

    asset4 = trade(ticker='AUDUSD=X', quantity_purchased=13581, date_purchased='2022-03-11', asset_type='FX',
                   leverage=20, short=False)

    asset5 = trade(ticker='AMD', quantity_purchased=94, date_purchased='2022-03-11', asset_type='equity',
                   leverage=1, short=False)

    alpha_fund = portfolio(asset1, asset2, asset3, asset4, asset5)
    print(alpha_fund.pnl())

    # for i in alpha_fund.asset_list:
    #     print(i.pnl())
