# === streamlit_app.py ===

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import os

# === Load Forecast Data ===
@st.cache_data
def load_data():
    csv_path = "Total_Forecast.csv"

    if not os.path.exists(csv_path):
        st.error(f"❌ File not found: {csv_path}")
        st.stop()

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    df["Date"] = pd.to_datetime(df["Date"])

    df.rename(columns={
        "CI Lower (30%)": "lower",
        "CI Upper (30%)": "upper"
    }, inplace=True)

    df["Type"] = df["Villa"].apply(lambda x: "Expense" if "Expense" in x else "Forecast")

    return df

# === Load Data
df = load_data()

# === Sidebar Filters
villa_list = df["Villa"].unique()
selected_villa = st.sidebar.selectbox("Select Villa", sorted(villa_list))

chart_type = st.sidebar.radio("Chart Type", ["Line Forecast", "Bar Forecast", "Table View"])
metric = st.sidebar.radio("Metric", ["Forecast", "lower", "upper"])
show_ci = st.sidebar.checkbox("Show Confidence Interval", value=True)

# === Filtered Data
villa_df = df[df["Villa"] == selected_villa].sort_values("Date")

# === Page Header
st.title("12-Month Forecast Dashboard")
st.subheader(f"{selected_villa} – {villa_df['Type'].iloc[0]}")

# === Formatter: Millions of Rupiah
def format_million(x, pos):
    return f'Rp {int(x / 1e6):,}M'.replace(",", ".")

# === Visualization
if chart_type == "Line Forecast":
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('#0a192f')
    ax.set_facecolor('#0a192f')

    ax.plot(villa_df["Date"], villa_df["Forecast"], label="Forecast", color="lime", linestyle="--", marker='o')

    if show_ci:
        ax.fill_between(
            villa_df["Date"],
            villa_df["lower"],
            villa_df["upper"],
            alpha=0.2,
            color="lime",
            label="Confidence Interval (±30%)"
        )

    ax.set_title(f"{selected_villa} – 12-Month Forecast", color='white')
    ax.set_ylabel("Revenue", color='white')
    ax.set_xlabel("Date", color='white')
    ax.grid(True, linestyle='--', linewidth=0.7, alpha=0.5, color='white')
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(format_million))

    for spine in ax.spines.values():
        spine.set_color('white')
    ax.tick_params(colors='white')
    ax.tick_params(axis="x", rotation=45)

    legend = ax.legend(loc="upper left", facecolor='#0a192f', edgecolor='white')
    for text in legend.get_texts():
        text.set_color("white")

    st.pyplot(fig)

elif chart_type == "Bar Forecast":
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('#0a192f')
    ax.set_facecolor('#0a192f')

    ax.bar(villa_df["Date"], villa_df[metric], color="skyblue")

    ax.set_title(f"{metric.capitalize()} over Time", color='white')
    ax.set_ylabel("Revenue", color='white')
    ax.set_xlabel("Date", color='white')
    ax.grid(True, linestyle='--', linewidth=0.7, alpha=0.5, color='white')
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(format_million))

    for spine in ax.spines.values():
        spine.set_color('white')
    ax.tick_params(colors='white')
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
