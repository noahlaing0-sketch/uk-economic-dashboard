import plotly.graph_objects as go
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

import streamlit as st
from calculations import build_merged_dataset, add_derived_metrics

st.set_page_config(page_title="UK Economic Conditions Dashboard", layout="wide")

st.title("UK Economic Conditions Dashboard")
st.write("Live UK inflation, wages, unemployment, and interest rate data with AI-assisted analysis.")


@st.cache_data(ttl=3600)
def load_data():
    df = build_merged_dataset()
    df = add_derived_metrics(df)
    return df


df = load_data()

st.write(f"Loaded {len(df)} months of data, from {df['date'].min().date()} to {df['date'].max().date()}")
st.dataframe(df.tail(10))
st.header("CPI Inflation")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df["date"],
    y=df["cpi_inflation_rate"],
    mode="lines",
    name="CPI Inflation (%)",
    line=dict(color="#4C9BE8", width=2),
))

fig.add_hline(
    y=2.0,
    line_dash="dash",
    line_color="gray",
    annotation_text="Bank of England 2% target",
    annotation_position="top left",
)

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Annual CPI Inflation (%)",
    hovermode="x unified",
)

st.plotly_chart(fig, use_container_width=True)

st.header("Interest Rates in Real Terms")
st.write(
    "The Bank Rate alone doesn't tell you how restrictive policy actually is. "
    "A 4% rate means something very different when inflation is 8% versus 2%. "
    "The real interest rate (Bank Rate minus inflation) shows the difference: "
    "when it's negative, money is effectively cheap despite high headline rates."
)

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=df["date"], y=df["bank_rate"],
    mode="lines", name="Bank Rate (%)",
    line=dict(color="#4C9BE8", width=2),
))

fig2.add_trace(go.Scatter(
    x=df["date"], y=df["cpi_inflation_rate"],
    mode="lines", name="CPI Inflation (%)",
    line=dict(color="#E8944C", width=2),
))

fig2.add_trace(go.Scatter(
    x=df["date"], y=df["real_interest_rate"],
    mode="lines", name="Real Interest Rate (%)",
    line=dict(color="#6BCB77", width=2, dash="dot"),
))

fig2.add_hline(y=0, line_dash="dash", line_color="gray")

fig2.update_layout(
    xaxis_title="Date",
    yaxis_title="Percent (%)",
    hovermode="x unified",
)

st.plotly_chart(fig2, use_container_width=True)

st.header("Bank Rate vs Simplified Taylor Rule")
st.write(
    "The Taylor Rule is a simple formula used to estimate what interest rate a "
    "central bank 'should' set, given inflation and economic slack. Comparing it "
    "to the actual Bank Rate shows periods where policy looked loose or tight "
    "relative to the rule. Note: this is a simplified version — the standard rule "
    "uses an output gap, which is out of scope here, so unemployment's deviation "
    "from its average is used as a rough proxy."
)

fig3 = go.Figure()

fig3.add_trace(go.Scatter(
    x=df["date"], y=df["bank_rate"],
    mode="lines", name="Actual Bank Rate (%)",
    line=dict(color="#4C9BE8", width=2),
))

fig3.add_trace(go.Scatter(
    x=df["date"], y=df["taylor_rule_rate"],
    mode="lines", name="Taylor Rule implied rate (%)",
    line=dict(color="#C77DFF", width=2, dash="dash"),
))

fig3.update_layout(
    xaxis_title="Date",
    yaxis_title="Percent (%)",
    hovermode="x unified",
)

st.plotly_chart(fig3, use_container_width=True)