import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Crypto Dashboard", layout="wide")

st.title("Real-Time Cryptocurrency Dashboard")
st.caption("Live data fetched by your Selenium scraper every 30 minutes.")

# Load data
data_file = "data/crypto_data_log.csv"
if not os.path.exists(data_file):
    st.warning("No data found yet. Run scraper.py to start collecting data.")
    st.stop()

df = pd.read_csv(data_file)
latest = df.groupby("Coin").last().reset_index()
st.subheader("Latest Market Overview")
st.dataframe(latest[["Coin", "Price", "Change_24h", "MarketCap", "Timestamp"]])

# Buy/Sell suggestions
def get_signal(change):
    if change > 5:
        return "🔥 Strong Buy"
    elif 1 < change <= 5:
        return "✅ Buy"
    elif -1 <= change <= 1:
        return "🟡 Hold"
    elif -5 <= change < -1:
        return "⚠️ Sell"
    else:
        return "🚨 Strong Sell"

latest["Signal"] = latest["Change_24h"].apply(get_signal)
st.subheader("Suggested Actions")
st.table(latest[["Coin", "Price", "Change_24h", "Signal"]])
st.subheader("Price Trend Over Time")
coin_choice = st.selectbox("Choose a Coin:", sorted(df["Coin"].unique()))
coin_df = df[df["Coin"] == coin_choice]

fig = px.line(coin_df, x="Timestamp", y="Price", title=f"{coin_choice} Price Trend", markers=True)
st.plotly_chart(fig, use_container_width=True)

# 24h Change Visualization
st.subheader("🔄 24h Percentage Change")
fig2 = px.bar(latest, x="Coin", y="Change_24h", color="Signal",
              title="24h Change & Signal", color_discrete_map={
                  "🔥 Strong Buy": "green", "✅ Buy": "lightgreen",
                  "🟡 Hold": "gray", "⚠️ Sell": "orange", "🚨 Strong Sell": "red"
              })
st.plotly_chart(fig2, use_container_width=True)

st.info("💾 Data auto-updates every 30 minutes via scraper.py. Refresh this page to see the latest stats.")
