import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
from src.data_analyse import get_event_units
from src.data_fetch import collect_all_results, fetch_year
from src.data_format import EVENT_MAPPINGS, format_athlete_best_results, seconds_to_hms_label
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

    all_results_df: pd.DataFrame | None = None
    trend_df: pd.DataFrame | None = None

    if not all_year_dfs:
        st.warning("No data available — please check site connectivity or try another event.")
    else:
        all_results_df = pd.concat(all_year_dfs, ignore_index=True)
        trend_df = pd.DataFrame(yearly_averages)

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

        if units == "seconds":
            ax.set_ylabel("Average Time (s)")
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(seconds_to_hms_label))
        elif units == "points":
            ax.set_ylabel(f"Average Points")
            ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:.0f}"))
        else:
            ax.set_ylabel(f"Average Distance ({units})")
            ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:.2f}"))

        ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        st.pyplot(fig)

        # build display column
        if units == "seconds":
            trend_df["AverageMark_display"] = trend_df["AverageMark"].apply(lambda x: seconds_to_hms_label(x, None))
            table_df = trend_df[["Year", "AverageMark_display"]].rename(columns={"AverageMark_display": "Average Performance"})
            with st.expander("View Data Table"):
                st.dataframe(table_df, width=800, hide_index=True)
        elif units == "points":
            table_df = trend_df[["Year", "AverageMark"]].rename(columns={"AverageMark": "Average Performance"})
            with st.expander("View Data Table"):
                st.dataframe(table_df.style.format({"Average Performance": "{:.0f}"}), width=600, hide_index=True)
        else:
            table_df = trend_df[["Year", "AverageMark"]].rename(columns={"AverageMark": "Average Performance"})
            with st.expander("View Data Table"):
                st.dataframe(table_df.style.format({"Average Performance": "{:.2f}"}), width=600, hide_index=True)

        with st.expander("View Athlete Rankings"):
            athlete_display = format_athlete_best_results(all_results_df, event_display_name)
            if not athlete_display.empty:
                if units == "seconds":
                    athlete_display["Best Result"] = athlete_display["Best Result"].apply(lambda x: seconds_to_hms_label(x, None))
                    athlete_display.rename(columns={"Best Result": "Best Performance"}, inplace=True)
                    st.dataframe(athlete_display, width=1200, hide_index=True, column_config={ "Profile Link": st.column_config.LinkColumn(label="Profile", display_text="🔗")})
                elif units == "points":
                    athlete_display.rename(columns={"Best Result": "Best Performance"}, inplace=True)
                    st.dataframe(athlete_display.style.format({"Best Performance": "{:.0f}"}), width=1200, hide_index=True, column_config={ "Profile Link": st.column_config.LinkColumn(label="Profile", display_text="🔗") })
                else:
                    athlete_display.rename(columns={"Best Result": "Best Performance"}, inplace=True)
                    st.dataframe(athlete_display.style.format({"Best Performance": "{:.2f}"}), width=1200, hide_index=True, column_config={ "Profile Link": st.column_config.LinkColumn(label="Profile", display_text="🔗") })
            else:
                st.warning("No athlete results to display.")

    else:
        st.warning("No data available — please check site connectivity or try another event.")
else:
    st.info("Configure your settings and click **Run Analysis** to begin.")
