from datetime import datetime, timedelta
import yfinance as yf

from utility.clean_data import clean_data


def liquidate(start, asset_dictionary):
    """
    :param start: Start date of portfolio
    :param asset_dictionary: Dictionary of asset tickers and quantity of asset held.
    :return: Current portfolios asset value if liquidated and the price over time.
    """

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
