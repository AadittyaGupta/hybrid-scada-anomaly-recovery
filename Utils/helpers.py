import pandas as pd

def load_data(file):
    """Load CSV file into pandas dataframe"""
    return pd.read_csv(file)


def convert_timestamp(df, column="timestamp"):
    """Convert timestamp column to datetime"""
    df[column] = pd.to_datetime(df[column])
    df = df.sort_values(by=column)
    return df