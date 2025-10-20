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

EVENT_MAPPINGS = {
    # Sprints
    "60 Metres": ("60-metres", "sprints", "both"),
    "100 Metres": ("100-metres", "sprints", "both"),
    "200 Metres": ("200-metres", "sprints", "both"),
    "400 Metres": ("400-metres", "sprints", "both"),

    # Middle / Long Distance
    "800 Metres": ("800-metres", "middlelong", "both"),
    "1500 Metres": ("1500-metres", "middlelong", "both"),
    "Mile": ("mile", "middlelong", "both"),
    "3000 Metres": ("3000-metres", "middlelong", "both"),
    "5000 Metres": ("5000-metres", "middlelong", "both"),
    "10000 Metres": ("10000-metres", "middlelong", "both"),

    # Road Running
    "Half Marathon": ("half-marathon", "road-running", "both"),
    "Marathon": ("marathon", "road-running", "both"),

    # Race Walks
    "50 Kilometres Race Walk": ("50-kilometres-race-walk", "race-walks", "both"),

    # Hurdles
    "60 Metres Hurdles": ("60-metres-hurdles", "hurdles", "both"),
    "100 Metres Hurdles": ("100-metres-hurdles", "hurdles", "women"),
    "110 Metres Hurdles": ("110-metres-hurdles", "hurdles", "men"),
    "400 Metres Hurdles": ("400-metres-hurdles", "hurdles", "both"),
    "3000 Metres Steeplechase": ("3000-metres-steeplechase", "hurdles", "both"),

    # Jumps
    "High Jump": ("high-jump", "jumps", "both"),
    "Long Jump": ("long-jump", "jumps", "both"),
    "Triple Jump": ("triple-jump", "jumps", "both"),
    "Pole Vault": ("pole-vault", "jumps", "both"),

    # Throws
    "Shot Put": ("shot-put", "throws", "both"),
    "Discus Throw": ("discus-throw", "throws", "both"),
    "Hammer Throw": ("hammer-throw", "throws", "both"),
    "Javelin Throw": ("javelin-throw", "throws", "both"),

    # Combined Events
    "Pentathlon": ("pentathlon", "combined-events", "women"),
    "Heptathlon": ("heptathlon", "combined-events", "women"),
    "Decathlon": ("decathlon", "combined-events", "men"),

    # Relays
    "4x100 Metres Relay": ("4x100-metres-relay", "relays"),
    "4x400 Metres Relay": ("4x400-metres-relay", "relays"),
}
