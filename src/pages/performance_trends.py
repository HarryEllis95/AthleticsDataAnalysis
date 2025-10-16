import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from src.data_fetch import fetch_toplist

st.title("Athletics Performance Trends")
st.write("Showing average of top 100 women's 100m performances (2014–2024).")

event_url_template = "https://worldathletics.org/records/toplists/sprints/100-metres/all/women/senior/{year}"

years = range(2014, 2025)
data_records = []

for year in years:
    st.write(f"Fetching {year}...")
    df = fetch_toplist(event_url_template.format(year=year))
    if df is None:
        continue

    df["Mark"] = pd.to_numeric(df["Mark"], errors="coerce")
    avg_mark = df["Mark"].head(100).mean()
    data_records.append({"Year": year, "AverageMark": avg_mark})

if data_records:
    trend_df = pd.DataFrame(data_records)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(trend_df["Year"], trend_df["AverageMark"], marker="o", linewidth=2)
    ax.set_title("Average of Top 100 Women's 100m Performances (2014–2024)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Average Time (seconds)")
    ax.grid(True)
    st.pyplot(fig)
else:
    st.warning("⚠️ No data available — check site connectivity.")
