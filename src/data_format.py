import re

import pandas as pd

# shouldn't be bad values included in the call but incase things like 10.84A or 9.97 w appear i.e not pure numerical values, these need cleaning
# to avoid error
def normalize_marks(df: pd.DataFrame) -> pd.DataFrame:
    if "Mark" not in df.columns:
        return df

    df["Mark_original"] = df["Mark"]
    df["Mark"] = (
        df["Mark"]
        .astype(str)
        .str.extract(r"([\d.]+)")   # keep only numbers and decimals regex
        .astype(float)
    )
    return df