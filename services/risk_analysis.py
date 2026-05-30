def classify_risk(df, patterns):
    """
    Assign risk levels based on:
    - Final anomaly count
    - Detected cyber patterns
    """

    # ---------------------------
    # Count anomalies (UPDATED)
    # ---------------------------
    if 'final_anomaly' in df.columns:
        anomaly_count = df['final_anomaly'].sum()
    else:
        anomaly_count = 0

    # ---------------------------
    # Risk logic
    # ---------------------------
    if anomaly_count > 50 or len(patterns) > 1:
        return "🔴 HIGH RISK - Possible Cyber Attack"

    elif anomaly_count > 10:
        return "🟡 MEDIUM RISK - Suspicious Activity"

    else:
        return "🟢 LOW RISK - Normal Behavior"