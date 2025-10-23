import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
from src.data_analyse import get_event_units
from src.data_fetch import fetch_year
from src.data_format import EVENT_MAPPINGS, format_athlete_best_results, seconds_to_hms_label, format_performance_value
from datetime import datetime
import matplotlib.ticker as mticker

Y_LABELS = {
    "seconds": "Average Time (s)",
    "points": "Average Points",
    "metres": "Average Distance (m)",
}

Y_FORMATTERS = {
    "seconds": mticker.FuncFormatter(seconds_to_hms_label),
    "points": mticker.StrMethodFormatter("{x:.0f}"),
    "metres": mticker.StrMethodFormatter("{x:.2f}"),
}

def show_dataframe(df: pd.DataFrame, width: int = 800):
    st.dataframe(df, width=width, hide_index=True)

# Page config
st.set_page_config(page_title = "Athletics Performance Trends", layout="wide", initial_sidebar_state="collapsed")
st.title("Athletics Performance Trends")
st.markdown("Analyse how average top performances in world athletics events evolve over time.")

# User Controls
st.markdown("### ⚙️ Configure Analysis")

gender = st.radio("Gender", ["men", "women"], horizontal=True)

filtered_events = [name for name, (_, _, g) in EVENT_MAPPINGS.items() if g in ("both", gender)]
event_display_name = st.selectbox("Event", filtered_events, index=0, width=400)
event_url_name, event_category, _ = EVENT_MAPPINGS[event_display_name]

current_year = datetime.now().year
years = list(range(2000, current_year + 1))
subcol1, subcol2 = st.columns(2, gap="small")
with subcol1:
    start_year = st.selectbox("Start Year", years, index=0, key="start_year", label_visibility="visible", width=200)
with subcol2:
    end_year = st.selectbox("End Year", years, index=len(years) - 1, key="end_year", label_visibility="visible", width=200)

top_x = st.number_input("Top X Performances", min_value=10, max_value=1000, value=100, step=10, width=400)

run_analysis = st.button("Run Analysis")

# initialize persistent storage
if "trend_df" not in st.session_state:
    st.session_state.trend_df = None
if "all_results_df" not in st.session_state:
    st.session_state.all_results_df = None


# Main analysis - fetch results and create dataframes
if run_analysis:
    years = range(start_year, end_year + 1)
    placeholder = st.empty()

    all_year_dfs = []
    yearly_averages = []

    for y in years:
        placeholder.markdown(f"⏳ Fetching **{y}**…")
        df = fetch_year(event_category, event_url_name, gender, y, top_x)
        if df is None or "Mark" not in df.columns:
            continue
        df["Year"] = y
        all_year_dfs.append(df)
        avg_mark = pd.to_numeric(df["Mark"], errors="coerce").head(top_x).mean()
        yearly_averages.append({"Year": y, "AverageMark": avg_mark})

    placeholder.empty()

    if not all_year_dfs:
        st.warning("No data available — please check site connectivity or try another event.")
    else:
        st.session_state.all_results_df = pd.concat(all_year_dfs, ignore_index=True)
        st.session_state.trend_df = pd.DataFrame(yearly_averages)

#  use session state values
trend_df = st.session_state.trend_df
all_results_df = st.session_state.all_results_df

# if all_results_df is not None:
#     print(f"✅ Total performances fetched: {len(all_results_df)}")

# Display Resuls
if trend_df is not None and not trend_df.empty:
    units = get_event_units(event_display_name)

    trend_df["Year"] = trend_df["Year"].astype(int)
    if units != "seconds":
        trend_df["AverageMark"] = trend_df["AverageMark"].round(2)

    # configure plot
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(trend_df["Year"], trend_df["AverageMark"], marker="o", linewidth=2, color="tab:blue")

    ax.set_title(f"Average of Top {top_x} {gender.title()} {event_display_name.replace('-', ' ')} Performances ({start_year}–{end_year})")
    ax.set_xlabel("Year")
    ax.grid(True)

    ax.set_ylabel(Y_LABELS.get(units, f"Average Performance ({units})"))
    ax.yaxis.set_major_formatter(Y_FORMATTERS.get(units, mticker.StrMethodFormatter("{x:.2f}")))

    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    st.pyplot(fig)

    # build display column
    trend_df["Average Performance"] = trend_df["AverageMark"].apply(lambda x: format_performance_value(x, units))
    display_df = trend_df[["Year", "Average Performance"]]

    with st.expander("View Data Table", expanded=True):
        show_dataframe(display_df)

    athlete_filter = st.text_input("Search Athletes", placeholder="Type a name...", key="athlete_filter")
    athlete_display = format_athlete_best_results(all_results_df, event_display_name) # DataFrame of sorted athletes
    if athlete_filter:
        filtered_athlete = athlete_display["Athlete"].str.contains(athlete_filter, case=False, na=False)
        athlete_display_filtered = athlete_display[filtered_athlete].copy()
    else:
        athlete_display_filtered = athlete_display.copy()

    with st.expander("View Athlete Rankings", expanded=True):
        if not athlete_display_filtered.empty:
            athlete_display_filtered["Best Performance"] = athlete_display_filtered["Best Performance"].apply(lambda x: format_performance_value(x, units))
            st.dataframe(athlete_display_filtered, width=1200, hide_index=True,
                column_config={
                    "Profile Link": st.column_config.LinkColumn(label="Profile", display_text="🔗")
                },
            )
        else:
            st.warning("No athlete results to display.")

    competitors = athlete_display_filtered["Athlete"].values.tolist()
    athlete_one  = st.selectbox("Select Athlete One", competitors, index=0, width=400)
    athlete_two = st.selectbox("Select Athlete Two", competitors, index=0, width=400)

    if athlete_one is not None or athlete_two is not None:
        run_comparison = st.button("Run Comparison")

elif run_analysis:
    st.warning("No data available — please check site connectivity or try another event.")
else:
    st.info("Configure your settings and click **Run Analysis** to begin.")
