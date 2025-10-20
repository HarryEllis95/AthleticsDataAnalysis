import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from src.data_fetch import fetch_toplist, build_event_url
from src.data_format import EVENT_MAPPINGS, collect_all_results, format_athlete_best_results
from datetime import datetime
import matplotlib.ticker as mticker
from matplotlib.ticker import MaxNLocator

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


# Main analysis
if run_analysis:
    st.markdown(
        f"### Comparing average of top **{top_x}** performances for **{gender}'s {event_display_name.replace('-', ' ')}** between **{start_year}** and **{end_year}**"
    )

    years = range(start_year, end_year + 1)

    placeholder = st.empty()

    def update_progress(year):
        placeholder.markdown(f"⏳ Fetching **{year}**...")
    all_results_df, trend_df = collect_all_results(
        event_category, event_url_name, gender, years, top_x, _progress_callback=update_progress
    )
    placeholder.empty()

# Display Resuls
    if trend_df is not None and not trend_df.empty:
        trend_df["Year"] = trend_df["Year"].astype(int)
        trend_df["AverageMark"] = trend_df["AverageMark"].round(2)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(trend_df["Year"], trend_df["AverageMark"], marker="o", linewidth=2, color="tab:blue")

        ax.set_title(
            f"Average of Top {top_x} {gender.title()} {event_display_name.replace('-', ' ')} Performances ({start_year}–{end_year})"
        )
        ax.set_xlabel("Year")
        ax.set_ylabel("Average Time (seconds)" if "metres" in event_display_name else "Average Distance")

        ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:.2f}"))
        # x-axis: integer years only
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:.0f}"))

        trend_df.rename(columns={"AverageMark": "Average Mark"}, inplace=True)
        ax.grid(True)

        st.pyplot(fig)

        with st.expander("View Data Table"):
            st.dataframe(trend_df, width=800, hide_index=True)  # display data table

        with st.expander("View Athlete Rankings"):
            athlete_display = format_athlete_best_results(all_results_df)
            if not athlete_display.empty:
                st.dataframe(athlete_display, width=800, hide_index=True)
            else:
                st.warning("No athlete results to display.")

    else:
        st.warning("No data available — please check site connectivity or try another event.")
else:
    st.info("Configure your settings and click **Run Analysis** to begin.")
