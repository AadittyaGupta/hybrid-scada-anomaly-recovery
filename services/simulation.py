# from curses import window


# def stream_data(df, step):
#     '''Simulate real-time data streaming by yielding chunks of the dataframe'''
#     return df.iloc[step:step+window]

def stream_data(df, start, window=20):
    """
    True streaming:
    Returns only NEW chunk instead of full history
    """
    end = start + window
    return df.iloc[start:end]


import numpy as np

def inject_attack(df, start):
    """
    Inject realistic cyber attacks
    """

    df = df.copy()

    # 🔴 MAJOR ATTACK (one time)
    if 200 <= start <= 220:
        df.loc[start:start+10, 'voltage'] += np.random.uniform(3, 6)

    # 🟡 MINOR ANOMALIES (random noise)
    if start % 50 == 0:
        df.loc[start:start+5, 'current'] += np.random.uniform(1, 2)

    # 🔵 SENSOR FREEZE (replay-like attack)
    if 300 <= start <= 320:
        df.loc[start:start+10, 'voltage'] = df.loc[start, 'voltage']

    return df