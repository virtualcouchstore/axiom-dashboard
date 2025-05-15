import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    return pd.read_csv("top_wallets_leaderboard.csv")

df = load_data()

st.title("Axiom Wallet Leaderboard Dashboard")
st.markdown("Explore wallet performance, volume, fees, and more with interactive filters and charts.")

# Sidebar Filters
st.sidebar.header("Filter Wallets")

min_trades = st.sidebar.slider("Minimum Trade Count", 0, int(df["trade_count"].max()), 0)
max_trades = st.sidebar.slider("Maximum Trade Count", 0, int(df["trade_count"].max()), int(df["trade_count"].max()))

min_volume = st.sidebar.number_input("Minimum Total Volume", value=0)
max_volume = st.sidebar.number_input("Maximum Total Volume", value=float(df["total_volume"].max()))

min_pnl = st.sidebar.number_input("Minimum Net PnL", value=float(df["net_pnl"].min()))
max_pnl = st.sidebar.number_input("Maximum Net PnL", value=float(df["net_pnl"].max()))

top_n_wallets = st.sidebar.slider("Top N Wallets by Volume", 10, len(df), 100)

# Filter data
filtered_df = df[
    (df["trade_count"] >= min_trades) &
    (df["trade_count"] <= max_trades) &
    (df["total_volume"] >= min_volume) &
    (df["total_volume"] <= max_volume) &
    (df["net_pnl"] >= min_pnl) &
    (df["net_pnl"] <= max_pnl)
].copy()

top_df = filtered_df.sort_values("total_volume", ascending=False).head(top_n_wallets)

# Add Solscan link column
top_df["Wallet Address"] = top_df["wallet_address"].apply(
    lambda x: f"[{x}](https://solscan.io/account/{x})"
)

# KPI Section
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Wallets Shown", len(top_df))
col2.metric("Total Volume", f"${top_df['total_volume'].sum():,.0f}")
col3.metric("Total Fees", f"${top_df['fees_usd'].sum():,.0f}")
col4.metric("Total Net PnL", f"${top_df['net_pnl'].sum():,.0f}")

# Wallet Table with HTML-rendered clickable red links
st.subheader("Filtered Wallets")
st.markdown("Wallet addresses below are clickable links to Solscan.")

# Create HTML table manually
html_rows = ""
for _, row in top_df.iterrows():
    addr = row["wallet_address"]
    link = f"https://solscan.io/account/{addr}"
    html_rows += f"""
        <tr>
            <td><a href="{link}" target="_blank" style="color:red;text-decoration:none;">{addr}</a></td>
            <td>{row['total_volume']:,}</td>
            <td>{row['fees_usd']:,}</td>
            <td>{row['net_pnl']:,}</td>
            <td>{row['trade_count']}</td>
        </tr>
    """

html_table = f"""
<table style="width:100%; border-collapse: collapse;">
    <thead>
        <tr>
            <th align="left">Wallet Address</th>
            <th align="left">Total Volume</th>
            <th align="left">Fees (USD)</th>
            <th align="left">Net PnL</th>
            <th align="left">Trades</th>
        </tr>
    </thead>
    <tbody>
        {html_rows}
    </tbody>
</table>
"""

st.markdown(html_table, unsafe_allow_html=True)


# Scatter Plot
st.subheader("Fees vs Net PnL")
fig1 = px.scatter(
    top_df,
    x="fees_usd",
    y="net_pnl",
    size="total_volume",
    color="trade_count",
    hover_data=["wallet_address"],
    title="Fees vs Net PnL",
)
st.plotly_chart(fig1, use_container_width=True)

# Histogram: Trade Count
st.subheader("Distribution of Trade Count")
fig2 = px.histogram(
    top_df,
    x="trade_count",
    nbins=40,
    title="Trade Count Distribution"
)
st.plotly_chart(fig2, use_container_width=True)

# Histogram: Net PnL
st.subheader("Distribution of Net PnL")
fig3 = px.histogram(
    top_df,
    x="net_pnl",
    nbins=40,
    title="Net PnL Distribution"
)
st.plotly_chart(fig3, use_container_width=True)

# Ratio Analysis
top_df["fee_per_trade"] = top_df["fees_usd"] / top_df["trade_count"]
top_df["pnl_per_trade"] = top_df["net_pnl"] / top_df["trade_count"]

st.subheader("PnL vs Fee Per Trade")
fig4 = px.scatter(
    top_df,
    x="fee_per_trade",
    y="pnl_per_trade",
    size="total_volume",
    color="trade_count",
    hover_data=["wallet_address"],
    title="PnL per Trade vs Fee per Trade"
)
st.plotly_chart(fig4, use_container_width=True)

# Download filtered results
st.download_button(
    label="Download Filtered Wallets as CSV",
    data=top_df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_wallets.csv",
    mime="text/csv",
)

