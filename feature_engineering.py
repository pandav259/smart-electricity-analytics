import numpy as np
import pandas as pd

def prepare_features(df):
    df = df.copy()

    df["month_sin"] = np.sin(2 * np.pi * df["date"].dt.month / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["date"].dt.month / 12)

    df["lag_1"] = df["units"].shift(1)
    df["lag_2"] = df["units"].shift(2)

    df["rolling_mean_3"] = df["units"].shift(1).rolling(window=3).mean()
    df["trend_index"] = range(len(df))

    df_model = df.dropna().copy()

    return df_model