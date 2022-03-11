import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime


class trade:

    def __init__(self, ticker, quantity_purchased, date_purchased, asset_type, date_sold=datetime.today(), leverage=1,
                 short=False, market='NYSE'):

        self.ticker = ticker
        self.quantity_purchased = quantity_purchased
        self.date_purchased = datetime.strptime(date_purchased, '%Y-%m-%d')
        self.asset_type = asset_type
        self.date_sold = date_sold
        self.leverage = leverage
        self.short = short

        asset = yf.Ticker(ticker)
        price_history = asset.history(self.ticker, start=self.date_purchased, end=self.date_sold)['Close']

        self.purchase_price = price_history[-1]
        self.price_history = price_history

        # If this is an equity we must define what market it is traded on. Usually NYSE.
        if asset_type == 'equity':
            self.market = market

            if self.date_sold.weekday() > 5:
                raise Exception('Invalid purchase date. Equities markets are closed on weekends.')

        # Sanity checks
        if date_sold is not None:

            if self.date_purchased > self.date_sold:
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

        price_change = (self.price_history[0] - self.price_history[-1])

        # Is short * quantity_purchased * price change * leverage = profit/loss.
        return np.sign((not self.short) - 0.5) * self.quantity_purchased * price_change * self.leverage

    def value(self, date=datetime.today()):

        asset = yf.Ticker(self.ticker)
        current_price = self.price_history[0]

        # Is short * quantity_purchased * price change * leverage = absolute profit/loss.
        return np.sign((not self.short) - 0.5) * self.quantity_purchased * current_price

    def graph(self):
        # TODO: Graph leverage properly.

        date_sold = self.date_sold

        if date_sold is None:
            date_sold = datetime.today()

        asset = yf.Ticker(self.ticker)
        price_history = self.quantity_purchased * asset.history(self.ticker, start=self.date_purchased, end=date_sold)[
            'Close']
        plt.plot(price_history, lw=1, color='black')
        plt.xticks(rotation=45)
        plt.subplots_adjust(bottom=0.21)
        plt.subplots_adjust(left=0.15)
        plt.xlabel('Date')
        plt.ylabel('Price (USD $)')
        plt.title(f'{self.ticker}')
        plt.show()


class portfolio:

    def __init__(self, *assets):
        self.asset_list = [*assets]
        self.cash = 0

    def add_trade(self, asset):
        self.asset_list.append(asset)

    def value(self):
        total_value = 0

        for asset in self.asset_list:
            total_value += asset.value()

        return self.cash + total_value


if __name__ == '__main__':

    initial_cash = 100000

    date_1 = '2022-02-24'
    date_2 = '2022-03-10'

    asset_1 = trade(ticker='GSK.L', quantity_purchased=6, date_purchased=date_1, asset_type='equity', leverage=1,
                    short=False)

    asset_2 = trade(ticker='UPST', quantity_purchased=77, date_purchased=date_1, asset_type='equity', leverage=1,
                    short=False)

    asset_3 = trade(ticker='HNT-USD', quantity_purchased=447, date_purchased=date_1, asset_type='equity',
                    leverage=1, short=False)

    asset_4 = trade(ticker='AUDUSD=X', quantity_purchased=13581, date_purchased=date_2, asset_type='FX',
                    leverage=20, short=False)

    asset_5 = trade(ticker='AMD', quantity_purchased=94, date_purchased=date_2, asset_type='equity',
                    leverage=1, short=False)

    alpha_fund = portfolio(asset_1, asset_2, asset_3, asset_4, asset_5)

    for asset in alpha_fund.asset_list:
        initial_cash -= asset.purchase_price * asset.quantity_purchased

    alpha_fund.cash = initial_cash
