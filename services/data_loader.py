import pandas as pd
import os

def load_full_dataset():
    # base_path = os.path.join(os.getcwd(), "Data")

    # Get project root (go one level up from services/)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Now point to Data folder
    base_path = os.path.join(base_dir, "Data")

    files = [
        "scada_chunk1.csv",
        "scada_chunk2.csv",
        "scada_chunk3.csv",
        "scada_chunk4.csv",
        "scada_chunk5.csv",
        "scada_chunk6.csv",
        "scada_chunk7.csv",
        "scada_chunk8.csv",
        "scada_chunk9.csv",
        "scada_chunk10.csv",
        "scada_chunk11.csv"
    ]

    df_list = []

    for file in files:
        file_path = os.path.join(base_path, file)
        df = pd.read_csv(file_path)
        df_list.append(df)

    full_df = pd.concat(df_list, ignore_index=True)

    return full_df