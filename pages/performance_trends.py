import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from src.data_fetch import fetch_toplist, build_event_url
from src.data_format import EVENT_MAPPINGS

# Page config
st.set_page_config(page_title = "Athletics Performance Trends", layout="wide", initial_sidebar_state="collapsed")
st.title("Athletics Performance Trends")
st.markdown("Analyse how average top performances in world athletics events evolve over time.")

# User Controls
st.markdown("### ⚙️ Configure Analysis")

col1, col2, col3 = st.columns([2,2,1])
with col1:
    gender = st.radio("Gender", ["men", "women"], horizontal=True)
    filtered_events = [name for name, (_, _, g) in EVENT_MAPPINGS.items() if g in ("both", gender)]
    event_display_name = st.selectbox("Event", filtered_events, index=0)
    event_url_name, event_category, _ = EVENT_MAPPINGS[event_display_name]
with col2:
    # define year range
    start_year, end_year = st.select_slider(
        "Select Year Range",
        options=list(range(2000, 2025)),
        value=(2015, 2024)
    )
with col3:
    top_x = st.number_input("Top X Performances", min_value=10, max_value=1000, value=100, step=10)
    run_analysis = st.button("Run Analysis")

@st.cache_data(show_spinner=False)
def get_data_for_year(event_category: str, event_name: str, gender: str, year: int, top_x: int):
    """Fetch and calculate average for a single year."""
    url = build_event_url(event_category, event_name, gender, year)
    df = fetch_toplist(url, amount=top_x)
    if df is None or "Mark" not in df.columns:
        return None
    df["Mark"] = pd.to_numeric(df["Mark"], errors="coerce")
    avg_mark = df["Mark"].head(top_x).mean()
    return {"Year": year, "AverageMark": avg_mark}

# Main analysis
if run_analysis:
    st.markdown(
        f"### Comparing average of top **{top_x}** performances for **{gender}'s {event_display_name.replace('-', ' ')}** between **{start_year}** and **{end_year}**"
    )

    years = range(start_year, end_year + 1)
    data_records = []

    # Spinner while fetching
    placeholder = st.empty()
    with st.spinner("Fetching data..."):
        for year in years:
            placeholder.markdown(f"⏳ Fetching **{year}**...")
            result = get_data_for_year(event_category, event_url_name, gender, year, top_x)
            if result:
                data_records.append(result)
        placeholder.empty()

# Display Resuls
    if data_records:
        trend_df = pd.DataFrame(data_records)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(trend_df["Year"], trend_df["AverageMark"], marker="o", linewidth=2, color="tab:blue")

        ax.set_title(
            f"Average of Top {top_x} {gender.title()} {event_display_name.replace('-', ' ')} Performances ({start_year}–{end_year})"
        )
        ax.set_xlabel("Year")
        ax.set_ylabel("Average Time (seconds)" if "metres" in event_display_name else "Average Distance")
        ax.grid(True)

        st.pyplot(fig)

        with st.expander("View Data Table"):
            st.dataframe(trend_df, use_container_width=True)
    else:
        st.warning("No data available — please check site connectivity or try another event.")
else:
    st.info("Configure your settings and click **Run Analysis** to begin.")
