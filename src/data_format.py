import re

import pandas as pd
import streamlit as st

from src.data_analyse import get_event_units
from src.data_fetch import build_event_url, fetch_toplist

# use streamlits in built caching - basically if func is called again with same arguments,
# don't rerun just return saved cahced result
@st.cache_data(show_spinner=False)
def collect_all_results(event_category: str, event_name: str, gender: str, years: range, top_x: int, _progress_callback=None):
    """Fetch and combine results for all selected years."""
    all_year_dfs = []
    yearly_averages = []

    for year in years:
        # always user to see which year's data is getting fetched
        if _progress_callback:
            _progress_callback(year)
        url = build_event_url(event_category, event_name, gender, year)
        df = fetch_toplist(url, amount=top_x)
        if df is None or "Mark" not in df.columns:
            continue

        df["Year"] = year
        all_year_dfs.append(df)

        avg_mark = pd.to_numeric(df["Mark"], errors="coerce").head(top_x).mean()
        yearly_averages.append({"Year": year, "AverageMark": avg_mark})

    if not all_year_dfs:
        return None, None

    combined_df = pd.concat(all_year_dfs, ignore_index=True)  # every scraped row for all requested years, concatenated
    trend_df = pd.DataFrame(yearly_averages)  # one row per year with the average of the top X marks
    return combined_df, trend_df

def format_athlete_best_results(all_results_df: pd.DataFrame, event_display_name: str) -> pd.DataFrame:
    """Return athletes ranked by their best performance"""
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
