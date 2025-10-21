import re
import time

import pandas as pd
from src.data_analyse import get_event_units

# Return athletes ranked by their best performance
def format_athlete_best_results(all_results_df: pd.DataFrame, event_display_name: str) -> pd.DataFrame:
    if all_results_df is None or all_results_df.empty:
        return pd.DataFrame()

    all_results_df["Mark"] = pd.to_numeric(all_results_df["Mark"], errors="coerce")

    units = get_event_units(event_display_name)
    if units in ("metres", "points"):
        agg_func = "max"       # higher is better
        ascending = False
    else:
        agg_func = "min"       # lower is better
        ascending = True

    athlete_best = (
        all_results_df
        .groupby(["Competitor", "Nat", "Competitor_link"], as_index=False)
        .agg(BestResult=("Mark", agg_func))
        .sort_values("BestResult", ascending=ascending)
    )

    athlete_best["Profile Link"] = athlete_best["Competitor_link"]

    athlete_display = athlete_best[["Competitor", "Nat", "Profile Link", "BestResult"]].rename(
        columns={
            "Competitor": "Athlete",
            "Nat": "Country",
            "BestResult": "Best Performance",
        }
    )
    return athlete_display

#Convert a time string (H:MM:SS, M:SS.xx, or S.xx) into total seconds (float)
def parse_time_to_seconds(value: str) -> float | None:
    if not isinstance(value, str) or not value.strip():
        return None
    parts = value.strip().split(":")
    try:
        if len(parts) == 3:
            # H:MM:SS.xx
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + float(s)
        elif len(parts) == 2:
            # M:SS.xx
            m, s = parts
            return int(m) * 60 + float(s)
        else:
            return float(parts[0])
    except ValueError:
        return None

# shouldn't be bad values included in the call but incase things like 10.84A or 9.97 w appear i.e not pure numerical values, these need cleaning
# to avoid error
def normalize_marks(df: pd.DataFrame) -> pd.DataFrame:
    if "Mark" not in df.columns:
        return df

    df["Mark_original"] = df["Mark"]

    # Try parsing numeric or time-like marks into seconds/metres/points
    def to_number(val):
        if isinstance(val, str) and ":" in val:
            return parse_time_to_seconds(val)
        else:
            try:
                return float(re.search(r"[\d.]+", str(val)).group())
            except Exception:
                return None

    df["Mark"] = df["Mark"].apply(to_number)
    return df

def seconds_to_hms_label(x, pos):
    if x is None or not isinstance(x, (int, float)):
        return ""
    if x >= 3600:
        return time.strftime("%H:%M:%S", time.gmtime(x))
    elif x >= 60:
        m, s = divmod(x, 60)
        if s.is_integer():
            return f"{int(m)}:{int(s):02d}"
        else:
            return f"{int(m)}:{s:05.2f}"
    else:
        return f"{x:.2f}"

EVENT_MAPPINGS = {
    # Sprints
    "60 Metres": ("60-metres", "sprints", "both"),
    "100 Metres": ("100-metres", "sprints", "both"),
    "200 Metres": ("200-metres", "sprints", "both"),
    "400 Metres": ("400-metres", "sprints", "both"),

    # Middle / Long Distance
    "800 Metres": ("800-metres", "middlelong", "both"),
    "1500 Metres": ("1500-metres", "middlelong", "both"),
    "Mile": ("one-mile", "middlelong", "both"),
    "3000 Metres": ("3000-metres", "middlelong", "both"),
    "5000 Metres": ("5000-metres", "middlelong", "both"),
    "10000 Metres": ("10000-metres", "middlelong", "both"),

    # Road Running
    "Half Marathon": ("half-marathon", "road-running", "both"),
    "Marathon": ("marathon", "road-running", "both"),

    # Race Walks
    "50 Kilometres Race Walk": ("50-kilometres-race-walk", "race-walks", "men"),
    "20 Kilometres Race Walk": ("20-kilometres-race-walk", "race-walks", "women"),

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
    "Heptathlon": ("heptathlon", "combined-events", "women"),
    "Decathlon": ("decathlon", "combined-events", "men"),

    # Relays
    "4x100 Metres Relay": ("4x100-metres-relay", "relays", "both"),
    "4x400 Metres Relay": ("4x400-metres-relay", "relays", "both"),
}
