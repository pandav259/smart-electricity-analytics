import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import RandomizedSearchCV

def train_models(X, y):
    tscv = TimeSeriesSplit(n_splits=3)

    lr_mae_scores = []
    lr_rmse_scores = []

    rf_mae_scores = []
    rf_rmse_scores = []

    for train_index, test_index in tscv.split(X):

        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

        # Linear Regression
        lr = LinearRegression()
        lr.fit(X_train, y_train)
        lr_preds = lr.predict(X_test)

        lr_mae_scores.append(mean_absolute_error(y_test, lr_preds))
        lr_rmse_scores.append(np.sqrt(mean_squared_error(y_test, lr_preds)))

        # Random Forest
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        rf_preds = rf.predict(X_test)

        rf_mae_scores.append(mean_absolute_error(y_test, rf_preds))
        rf_rmse_scores.append(np.sqrt(mean_squared_error(y_test, rf_preds)))

    comparison_df = pd.DataFrame({
        "Model": ["Linear Regression", "Random Forest"],
        "MAE": [np.mean(lr_mae_scores), np.mean(rf_mae_scores)],
        "RMSE": [np.mean(lr_rmse_scores), np.mean(rf_rmse_scores)]
    })

    param_dist = {
        "n_estimators": [50, 100, 200],
        "max_depth": [None, 3, 5, 7],
        "min_samples_split": [2, 4, 6],
        "min_samples_leaf": [1, 2, 3]
    }

    rf = RandomForestRegressor(random_state=42)

    random_search = RandomizedSearchCV(
        rf,
        param_distributions=param_dist,
        n_iter=10,
        cv=tscv,
        scoring="neg_mean_absolute_error",
        random_state=42
    )

    random_search.fit(X, y)
    rf_final = random_search.best_estimator_
    best_params = random_search.best_params_

    return rf_final, comparison_df, best_params


def recursive_forecast(rf_final, df_model, forecast_steps=3):
    last_row = df_model.iloc[-1].copy()
    future_predictions = []

    for step in range(forecast_steps):

        next_month = (last_row["date"].month % 12) + 1

        month_sin = np.sin(2 * np.pi * next_month / 12)
        month_cos = np.cos(2 * np.pi * next_month / 12)

        input_features = pd.DataFrame([{
            "lag_1": last_row["units"],
            "lag_2": last_row["lag_1"],
            "rolling_mean_3": (
                last_row["units"] +
                last_row["lag_1"] +
                last_row["lag_2"]
            ) / 3,
            "month_sin": month_sin,
            "month_cos": month_cos,
            "trend_index": last_row["trend_index"] + 1
        }])

        prediction = rf_final.predict(input_features)[0]
        future_predictions.append(prediction)

        # Update last row
        last_row["lag_2"] = last_row["lag_1"]
        last_row["lag_1"] = prediction
        last_row["units"] = prediction
        last_row["date"] = last_row["date"] + pd.DateOffset(months=1)
        last_row["trend_index"] += 1

    # Create future dates
    last_date = df_model["date"].max()
    future_dates = [
        last_date + pd.DateOffset(months=i)
        for i in range(1, forecast_steps + 1)
    ]

    forecast_df = pd.DataFrame({
        "date": future_dates,
        "predicted_units": future_predictions
    })

    return forecast_df, future_predictions