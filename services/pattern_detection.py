def detect_patterns(df):
    """
    Detect suspicious cyber-related patterns
    Uses final_anomaly column
    """
    patterns = []

    # ---------------------------
    # Pattern 1: Burst anomalies (possible coordinated attack)
    # ---------------------------
    if 'final_anomaly' in df.columns:
        burst = df['final_anomaly'].rolling(window=5).sum()

        if (burst > 3).any():
            patterns.append("⚠️ Burst anomaly pattern (Possible coordinated attack)")

    # ---------------------------
    # Pattern 2: Sudden spike (voltage manipulation)
    # ---------------------------
    if 'voltage_diff' in df.columns:
        spikes = df[df['voltage_diff'].abs() > 2]

        if len(spikes) > 5:
            patterns.append("⚠️ Sudden voltage manipulation detected")

    # ---------------------------
    # Pattern 3: Flatline (sensor tampering)
    # ---------------------------
    if 'voltage' in df.columns:
        flat = df['voltage'].rolling(window=10).std()

        if (flat < 0.01).any():
            patterns.append("⚠️ Possible sensor freeze / tampering")

    return patterns