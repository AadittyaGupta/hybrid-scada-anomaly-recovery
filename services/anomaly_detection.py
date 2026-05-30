from sklearn.ensemble import IsolationForest
import numpy as np

def train_isolation_forest(df):
    model = IsolationForest(contamination=0.02, random_state=42)
    model.fit(df)
    return model


def detect_anomalies(model, df):

    df = df.copy()

    # ---------------------------
    # 1. ML-based anomaly
    # ---------------------------
    df['ml_anomaly'] = model.predict(df)  # -1 = anomaly

    # ---------------------------
    # 2. Z-score per column
    # ---------------------------
    z_scores = np.abs((df - df.mean()) / df.std())

    # If ANY feature crosses threshold → anomaly
    df['stat_anomaly'] = (z_scores > 2).any(axis=1)

    # ---------------------------
    # 3. Final anomaly (STRICT)
    # ---------------------------
    df['final_anomaly'] = (
        (df['ml_anomaly'] == -1) | (df['stat_anomaly'] == True)
    )

    return df