

def current_allocation(portfolio_cash, df):
    """
    :param portfolio_cash: Initial cash when portfolio began.
    :param df: Dataframe of the portfolio, imported csv file.
    :return: Portfolios cash holdings and a dictionary of assets with quantity held.
    """

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
