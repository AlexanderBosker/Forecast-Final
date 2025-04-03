# === streamlit_app.py ===

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

@st.cache_data
def load_data():
    csv_path = "Total_Forecast.csv"
    
    st.write("Checking for file:", csv_path)
    if not os.path.exists(csv_path):
        st.error(f"File not found: {csv_path}")
        st.stop()

    with open(csv_path, "rb") as f:
        header = f.read(500)
    st.write("File starts with (first 500 bytes):", header[:300])  # Partial preview

    df = pd.read_csv(csv_path, parse_dates=["Date"])
    df.rename(columns={
        "CI Lower (30%)": "lower",
        "CI Upper (30%)": "upper"
    }, inplace=True)
    if "Type" not in df.columns:
        df["Type"] = "Forecast"

    return df

df = load_data()

# Sidebar Filters
villa_list = df["Villa"].unique()
selected_villa = st.sidebar.selectbox("Select Villa", sorted(villa_list))

chart_type = st.sidebar.radio("Chart Type", ["Line Forecast", "Bar Forecast", "Table View"])
metric = st.sidebar.radio("Metric", ["Forecast", "lower", "upper"])
show_ci = st.sidebar.checkbox("Show Confidence Interval", value=True)

# Villa-Specific Data
villa_df = df[df["Villa"] == selected_villa].sort_values("Date")

# Page Title
st.title("12-Month Forecast Dashboard")
st.subheader(f"{selected_villa} – {villa_df['Type'].iloc[0]}")

# Visualization
if chart_type == "Line Forecast":
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(villa_df["Date"], villa_df["Forecast"], label="Forecast", color="lime")

    if show_ci:
        ax.fill_between(
            villa_df["Date"],
            villa_df["lower"],
            villa_df["upper"],
            alpha=0.3,
            color="lime",
            label="±30% CI"
        )

    ax.set_title("Forecast with Confidence Interval")
    ax.set_ylabel("Amount (Rp)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.tick_params(axis="x", rotation=45)
    st.pyplot(fig)

elif chart_type == "Bar Forecast":
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(villa_df["Date"], villa_df[metric], color="skyblue")
    ax.set_title(f"{metric} over Time")
    ax.set_ylabel("Amount (Rp)")
    ax.tick_params(axis="x", rotation=45)
    st.pyplot(fig)

else:
    st.dataframe(
        villa_df[["Date", "Forecast", "lower", "upper"]]
        .style
        .format({
            "Forecast": "Rp {:,.0f}",
            "lower": "Rp {:,.0f}",
            "upper": "Rp {:,.0f}"
        })
    )

