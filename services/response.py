import pandas as pd


def apply_response(df, anomalies):

    df = df.copy()
    numeric_cols = df.select_dtypes(include=['number']).columns

    for idx in anomalies.index:

        # ⚠️ Skip if index not present (extra safety)
        if idx not in df.index:
            continue

        # 🔥 Detect severity
        severity = "minor"

        for col in numeric_cols:
            if abs(df.loc[idx, col]) > 2:
                severity = "major"
                break

        for col in numeric_cols:

            try:
                prev_idx = idx - 1

                # 🟡 MINOR → slight smoothing
                if severity == "minor":             

                    if prev_idx in df.index:
                        prev_val = df.loc[prev_idx, col]
                        curr_val = df.loc[idx, col]             

                        # gentle correction
                        df.loc[idx, col] = 0.8 * prev_val + 0.2 * curr_val              


                # 🔴 MAJOR → strong recovery (but realistic)
                else:               

                    # if prev_idx in df.index:
                    #     prev_val = df.loc[prev_idx, col]                

                    #     # snap back towards normal (not zero!)
                    #     df.loc[idx, col] = prev_val             

                    # else:
                    #     # fallback (first row case)
                    #     df.loc[idx, col] = df[col].mean()

                    if prev_idx in df.index:
                        prev_val = df.loc[prev_idx, col]
                        curr_val = df.loc[idx, col]

                        # gradual correction instead of instant snap
                        df.loc[idx, col] = 0.6 * prev_val + 0.4 * curr_val

                    else:
                        df.loc[idx, col] = df[col].mean()

                if col == "voltage":
                    df.loc[idx, col] = max(df.loc[idx, col], 180)

            except Exception:
                # fallback SAFE (no iloc!)
                df.loc[idx, col] = df.loc[idx, col]

    return df