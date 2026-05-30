# import pandas as pd
# from sklearn.preprocessing import StandardScaler

# def fix_timestamp(ts):
#     """
#     Fix invalid timestamps like 24:00:00 → next day 00:00:00
#     """
#     if "24:" in ts:
#         date_part = ts.split(" ")[0]
#         # Convert to next day
#         new_date = pd.to_datetime(date_part) + pd.Timedelta(days=1)
#         return str(new_date.date()) + " 00:00:00"
#     return ts


# def preprocess_data(df):
#     """
#     Clean and preprocess SCADA data
#     """
#     df = df.copy()

#     # Handle missing values
#     df = df.fillna(method='ffill')

#     # Fix timestamp errors BEFORE conversion
#     if 'timestamp' in df.columns:
#         df['timestamp'] = df['timestamp'].astype(str).apply(fix_timestamp)
#         df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

#     # Drop rows where timestamp still failed
#     df = df.dropna(subset=['timestamp'])

#     # Select numerical columns only
#     numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns

#     # Feature Engineering (basic)
#     for col in numeric_cols:
#         df[f"{col}_rolling_mean"] = df[col].rolling(window=3).mean()
#         df[f"{col}_diff"] = df[col].diff()

#     df = df.fillna(0)

#     # Normalize
#     scaler = StandardScaler()
#     df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

#     return df, scaler





































import pandas as pd
from sklearn.preprocessing import StandardScaler

def preprocess_data(df):

    df = df.copy()
    df = df.fillna(method='ffill')

    if 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        df = df.dropna(subset=['Timestamp'])

    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns

    # Feature Engineering
    for col in numeric_cols:
        df[f"{col}_diff"] = df[col].diff()
        df[f"{col}_rolling_mean"] = df[col].rolling(3).mean()

    # df = df.fillna(0)
    df = df.fillna(method='bfill').fillna(method='ffill')

    scaler = StandardScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

    return df, scaler