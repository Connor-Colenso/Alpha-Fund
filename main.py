# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import numpy as np


def current_allocation(portfolio_cash, df):
    asset_list = list(df['Ticker'])
    asset_dictionary = dict(zip(asset_list, [0] * len(asset_list)))

    for quantity, ticker, held, trade_price in zip(df['Quantity'], df['Ticker'], df['BUY/SELL'], df['Trade Price']):

        if held == 'BUY':
            asset_dictionary[ticker] += quantity
            portfolio_cash -= quantity * trade_price

        if held == 'SELL':
            asset_dictionary[ticker] -= quantity
            portfolio_cash += quantity * trade_price

    return portfolio_cash, asset_dictionary


def liquidate(start, asset_dictionary):

    end = datetime.today().strftime('%Y-%m-%d')
    tickers = ' '.join(list(asset_dictionary))
    data = yf.download(tickers, start=start, end=end)
    adj_close = data['Adj Close']

    portfolio_value = 0

    tmp_ticker = adj_close.columns[0]
    series_summed = adj_close[tmp_ticker].copy()
    series_summed[adj_close.index] = 0

    for ticker in asset_dictionary:
        df_tmp = clean_data(adj_close[ticker].ffill())
        portfolio_value += df_tmp[-1] * asset_dictionary[ticker]

        # pd.sum not working, not sure why.
        for date in df_tmp.index:
            series_summed[date] += df_tmp[date] * asset_dictionary[ticker]

    return portfolio_value, series_summed


def clean_data(df):
    for date, price in zip(df.index[::-1], list(df)[::-1]):

        if np.isnan(price):
            df[date] = prior_price

        prior_price = price

    return df


if __name__ == '__main__':
    portfolio_cash = 100000

    start_date = '2022-02-24'

    df = pd.read_csv('Alpha Fund - Sheet1.csv')
    portfolio_cash, asset_dictionary = current_allocation(portfolio_cash, df)
    portfolio_value, assets_over_time = liquidate(start_date, asset_dictionary)

    portfolio_liquidation_value = portfolio_cash + portfolio_value

    plt.plot(portfolio_cash + assets_over_time)
    print(asset_dictionary)
    plt.xticks(rotation=45)
    plt.subplots_adjust(bottom=0.21)
    plt.xlabel('Date')
    plt.ylabel('Price (USD $)')
    plt.title('Alpha Fund Portfolio')
    plt.show()
