# def explain_anomaly(df, idx):
#     '''Explain why a specific data point was flagged as an anomaly'''

#     row = df.loc[idx]

#     explanation = []

#     for col in df.columns:
#         if col != 'Timestamp':
#             if abs(row[col]) > 2:
#                 explanation.append(f"{col} deviated significantly")

#     return explanation            





# def explain_anomaly(df, idx):

#     explanation = []

#     numeric_cols = df.select_dtypes(include=['number']).columns

#     for col in numeric_cols:

#         mean = df[col].mean()
#         std = df[col].std()

#         if std == 0:
#             continue

#         z_score = abs((df.loc[idx, col] - mean) / std)

#         if z_score > 2:
#             explanation.append(f"{col} abnormal (z={round(z_score,2)})")

#     return explanation








def explain_anomaly(df, idx):

    explanation = []

    numeric_cols = df.select_dtypes(include=['number']).columns

    for col in numeric_cols:

        mean = df[col].mean()
        std = df[col].std()

        if std == 0:
            continue

        value = df.loc[idx, col]
        z_score = abs((value - mean) / std)

        # 🔥 LOWER threshold (important)
        if z_score > 1.5:
            explanation.append(f"{col} abnormal (z={round(z_score,2)})")

    # ✅ fallback (VERY IMPORTANT)
    if not explanation:
        explanation.append("Minor anomaly detected (model-based)")

    return explanation