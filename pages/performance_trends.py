import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from src.data_fetch import fetch_toplist, build_event_url

# Page config
st.set_page_config(page_title = "Athletics Performance Trends", layout="wide")
st.title("Athletics Performance Trends")
st.markdown(
    "Analyse how average top performances in world athletics events evolve over time."
)

# User Controls
st.sidebar.header("Analysis Settings")

event_category = st.sidebar.selectbox(
    "Event Category",
    ["sprints", "hurdles", "middle-distance", "long-distance", "jumps", "throws"],
    index=0
)

event_name = st.sidebar.selectbox(
    "Event Name",
    [
        "100-metres",
        "200-metres",
        "400-metres",
        "800-metres",
        "1500-metres",
        "5000-metres",
        "long-jump",
        "triple-jump",
        "shot-put",
    ],
    index=0,
)

gender = st.sidebar.radio("Gender", ["men", "women"], horizontal=True)

# define year range
start_year, end_year =  st.sidebar.select_slider(
    "Select Year Range",
    options=list(range(2000, 2025)),
    value=(2015, 2024)
)

top_x = st.sidebar.number_input(
    "Average over Top X Performances", min_value=10, max_value=1000, value=100, step=10
)

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
if st.button("Run Analysis"):
    st.markdown(
        f"### 📊 Comparing average of top **{top_x}** performances for **{gender}'s {event_name.replace('-', ' ')}** between **{start_year}** and **{end_year}**"
    )

    years = range(start_year, end_year)
    data_records = []

    # Spinner while fetching
    placeholder = st.empty()
    with st.spinner("Fetching data..."):
        for year in years:
            placeholder.markdown(f"⏳ Fetching **{year}**...")
            result = get_data_for_year(event_category, event_name, gender, year, top_x)
            if result:
                data_records.append(result)
        placeholder.empty()

# Display Resuls
    if data_records:
        trend_df = pd.DataFrame(data_records)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(trend_df["Year"], trend_df["AverageMark"], marker="o", linewidth=2, color="tab:blue")

        ax.set_title(
            f"Average of Top {top_x} {gender.title()} {event_name.replace('-', ' ')} Performances ({start_year}–{end_year})"
        )
        ax.set_xlabel("Year")
        ax.set_ylabel("Average Time (seconds)" if "metres" in event_name else "Average Distance")
        ax.grid(True)

        st.pyplot(fig)

        with st.expander("View Data Table"):
            st.dataframe(trend_df, use_container_width=True)
    else:
        st.warning("⚠️ No data available — please check site connectivity or try another event.")
else:
    st.info("👈 Configure your settings on the left and click **Run Analysis** to begin.")
