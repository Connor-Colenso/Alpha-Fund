import numpy as np


def clean_data(df):
    """
    :param df: Dataframe to be cleaned.
    :return: Cleaned dataframe.
    """
    for date, price in zip(df.index[::-1], list(df)[::-1]):

        if np.isnan(price):
            df[date] = prior_price

        prior_price = price

    return df
