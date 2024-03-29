import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta


class Trade:
    """
    Individual trade that can be placed into the Portfolio object. Data is sourced using Yahoo Finance.
    """

    def __init__(self, *, ticker, quantity, date_purchased, asset_type, date_sold=datetime.today(), leverage=1,
                 short=False, market='NYSE'):

        self.ticker = ticker
        self.quantity = quantity
        self.asset_type = asset_type
        self.date_sold = date_sold
        self.leverage = leverage
        self.short = short

        # Check that the date is in the correct format and convert to datetime if it's a string.
        if isinstance(date_purchased, str):
            self.date_purchased = datetime.strptime(date_purchased, '%Y-%m-%d')
        elif isinstance(date_purchased, datetime):
            self.date_purchased = date_purchased.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            raise Exception('Invalid type for date_purchased.')

        if isinstance(date_sold, str):
            self.date_sold = datetime.strptime(date_sold, '%Y-%m-%d')
        elif isinstance(date_sold, datetime):
            self.date_sold = date_sold.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            raise Exception('Invalid type for date_sold.')

        asset = yf.Ticker(ticker)
        price_history = asset.history(self.ticker, start=self.date_purchased, end=self.date_sold)['Close']

        if len(price_history) == 0:
            raise Exception('Price history is empty.')

        if price_history.index[0] != self.date_purchased:
            raise Exception(f'Invalid date range for {self.ticker} asset. Oldest date is {price_history.index[0]}.')

        self.purchase_price = price_history[0]

        # Fill in the date gaps for dates when market is closed with NaN and then backfill those gaps with future
        # values. This is essential for ensuring that the graphing of the portfolio can be done correctly as some
        # assets are traded 24/7 i.e. crypto.
        price_history = price_history.resample('1D').mean().ffill()
        percentage_return = (1 + self.leverage * np.sign((not self.short) - 0.5) * (
                price_history - self.purchase_price) / self.purchase_price)

        self.valuation_history = self.quantity * self.purchase_price * percentage_return
        self.percentage_return = percentage_return

        # If this is an equity we must define what market it is traded on. Usually NYSE.
        if asset_type == 'equity':
            self.market = market

            # Equities are not traded on weekends.
            if self.date_sold.weekday() > 5:
                raise Exception('Invalid purchase date. Equities markets are closed on weekends.')

        # Sanity checks
        if self.date_purchased > self.date_sold:
            raise Exception('Date sold is before date purchased.')

        if quantity <= 0:
            raise Exception('Quantity purchased is negative or 0.')

        if leverage <= 0:
            raise Exception('Leverage is negative or 0.')

        if not isinstance(short, bool):
            raise Exception('Short should be a boolean value.')

    def __repr__(self):
        return self.ticker

    def value(self):
        """
        :return: Current value of this asset of liquidated.
        """
        return self.valuation_history[0]

    def graph(self):
        """
        :return: None
        """
        price_history = self.quantity * self.valuation_history
        plt.plot(price_history, lw=1, color='black')
        plt.xticks(rotation=45)
        plt.subplots_adjust(bottom=0.21)
        plt.subplots_adjust(left=0.15)
        plt.xlabel('Date')
        plt.ylabel('Value (USD $)')
        plt.title(self.ticker)
        plt.show()


class Portfolio:
    """
    Portfolio object, can hold an arbitrary number of assets or pure cash.
    """

    def __init__(self, *, initial_cash, assets):
        self.asset_list = assets
        self.initial_cash = initial_cash

    def cash_history(self):
        """
        :return: Cash in the portfolio over time.
        """

        purchase_list = [asset.date_purchased for asset in self.asset_list]
        oldest_purchase = min(purchase_list)

        cash_dates = pd.date_range(oldest_purchase, datetime.today() - timedelta(days=1), freq='D')
        df = pd.DataFrame([self.initial_cash] * len(cash_dates)).set_index(cash_dates)
        df.columns = ['initial_cash']

        cash_list = []

        for asset in self.asset_list:

            if asset.date_sold == today():
                date_sold = today() - timedelta(days=1)
            else:
                date_sold = asset.date_sold

            cash_dates = pd.date_range(asset.date_purchased, date_sold, freq='D')
            tmp_df = pd.DataFrame([-asset.purchase_price * asset.quantity] * len(cash_dates)).set_index(cash_dates)
            tmp_df.columns = [asset.ticker]

            cash_list.append(tmp_df)

        cash_history = pd.concat([df] + cash_list, axis=1).fillna(0)
        cash_history['sum'] = cash_history.sum(axis=1)

        return cash_history['sum']

    def cash(self):
        """
        :return: Current cash held in the portfolio.
        """
        return self.cash_history()[-1]

    def add_trade(self, asset):
        """
        :param asset: Asset in the form of a Trade object.
        :return: None
        """
        self.asset_list.append(asset)

    def value(self):
        """
        :return: Value of the portfolio at the present time.
        """

        return self.portfolio_valuation()['sum'][-1]

    def portfolio_valuation(self):
        """
        :return: DataFrame containing the padded portfolios value over time. If a date has no data then it will check
        backwards in time until itn finds valid data to substitute.
        """

        df = pd.concat([asset.valuation_history for asset in self.asset_list] + [self.cash_history()], axis=1)
        df.columns = [asset.ticker for asset in self.asset_list] + ['CASH']
        df['sum'] = df.sum(axis=1)

        row_to_drop = 0
        for i in range(len(df), 0, -1):
            if df[i - 1:i].isnull().values.any():
                row_to_drop += 1
            else:
                break

        return df[0:len(df) - row_to_drop].fillna(0)

    def abs_return_graph(self, name):

        plt.plot(self.portfolio_valuation().index, self.portfolio_valuation()['sum'], lw=1, color='black')
        plt.xticks(rotation=45)
        plt.subplots_adjust(bottom=0.21)
        plt.subplots_adjust(left=0.15)
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value (USD $)')
        plt.title(name)
        plt.savefig(f'{name} - portfolio value.png', dpi=100)
        plt.show()

    def pct_return_graph(self, benchmark, name):
        """
        :param benchmark: Benchmark asset to compare against. Usually the FTSE100 or S&P500.
        :param name: Name of the graph and image name.
        :return: None
        """

        portfolio_pct_return = self.portfolio_valuation()['sum'].pct_change()

        purchase_list = [asset.date_purchased for asset in self.asset_list]
        oldest_purchase = min(purchase_list)

        asset = yf.Ticker(benchmark).history(start=oldest_purchase, end=today())['Close']

        benchmark_pct_return = asset.pct_change()

        plt.plot(self.portfolio_valuation().index, portfolio_pct_return, lw=1, color='black',
                 label='Portfolio Returns')

        plt.plot(benchmark_pct_return.index, benchmark_pct_return, lw=1, color='green',
                 label=f'Benchmark Returns ({benchmark})')

        plt.legend()
        plt.xticks(rotation=45)
        plt.subplots_adjust(bottom=0.21)
        plt.subplots_adjust(left=0.15)
        plt.xlabel('Date')
        plt.ylabel('Percentage Return (%)')
        plt.title(name)
        plt.savefig(f'{name} - pct return.png', dpi=100)
        plt.show()

    def pie_chart(self, name):
        """
        :param name: Name of the chart and image name.
        :return: None
        """

        df = self.portfolio_valuation()

        labels = []
        values = []

        for column in df:

            if column != 'sum':

                labels.append(column)
                values.append(df[column][-1])

        plt.pie(x=values, labels=labels, autopct='%1.1f%%')
        plt.title(name)
        plt.savefig(f'{name} - pie chart.png', dpi=100)
        plt.show()


def today():
    """
    :return: Datetime object of todays date. All other attributes are set to zero out.
    """
    return datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)


if __name__ == '__main__':

    initial_cash = 100000
    assets = []

    csv = pd.read_csv('Alpha Fund - Sheet1.csv')

    for index, row in csv.iterrows():

        date_sold = row['Date Sold']

        if np.isnan(date_sold):
            date_sold = today()

        assets.append(Trade(ticker=row['Ticker'],
                            quantity=row['Quantity'],
                            date_purchased=row['Purchase Date'],
                            date_sold=date_sold,
                            asset_type=row['Asset Type'],
                            leverage=row['Leverage'],
                            short=row['Short']))

    alpha_fund = Portfolio(initial_cash=initial_cash, assets=assets)

    alpha_fund.pct_return_graph(benchmark='^FTSE', name='Alpha Fund Portfolio')
    alpha_fund.pie_chart(name='Alpha Fund Portfolio')
    alpha_fund.abs_return_graph(name='Alpha Fund Portfolio')
