def detect_anomalies(model, X, df_model):
    df_model = df_model.copy()
    predictions = model.predict(X)

    df_model["predicted"] = predictions
    df_model["residual"] = df_model["units"] - predictions

    threshold = 2 * df_model["residual"].std()

    df_model["anomaly"] = abs(df_model["residual"]) > threshold

    anomalies = df_model[df_model["anomaly"]]

    return df_model, anomalies