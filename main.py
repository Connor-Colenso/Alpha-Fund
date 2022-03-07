import matplotlib.pyplot as plt
import pandas as pd

from utility.current_allocation import current_allocation
from utility.liquidate import liquidate

if __name__ == '__main__':
    portfolio_cash = 100000

    start_date = '2022-02-24'

    df = pd.read_csv('Alpha Fund - Sheet1.csv')
    portfolio_cash, asset_dictionary = current_allocation(portfolio_cash, df)
    portfolio_value, assets_over_time = liquidate(start_date, asset_dictionary)

    portfolio_liquidation_value = portfolio_cash + portfolio_value

    plt.plot(portfolio_cash + assets_over_time)
    plt.xticks(rotation=45)
    plt.subplots_adjust(bottom=0.21)
    plt.xlabel('Date')
    plt.ylabel('Price (USD $)')
    plt.title('Alpha Fund Portfolio')
    plt.show()
