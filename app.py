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

def latest_value(column):
    """
    Returns the most recent non-missing value for a column, the previous one,
    and its date. Indicators publish at different speeds, so each has its own
    latest available month.
    """
    series = df[["date", column]].dropna()
    if len(series) < 2:
        return None, None, None
    latest_row = series.iloc[-1]
    previous_row = series.iloc[-2]
    return latest_row[column], previous_row[column], latest_row["date"]


st.caption(
    f"{len(df)} months loaded · indicators publish at different times, "
    "so each shows its own latest available month"
)

col1, col2, col3, col4 = st.columns(4)


def show_metric(column_obj, label, series_name, fmt="{:.1f}", delta_color="normal"):
    current, previous, date = latest_value(series_name)
    if current is None:
        column_obj.metric(label, "n/a")
        return
    column_obj.metric(
        label,
        fmt.format(current) + "%",
        f"{current - previous:+.2f} pp",
        delta_color=delta_color,
    )
    column_obj.caption(date.strftime("%b %Y"))


show_metric(col1, "CPI Inflation", "cpi_inflation_rate", delta_color="inverse")
show_metric(col2, "Bank Rate", "bank_rate", fmt="{:.2f}", delta_color="off")
show_metric(col3, "Real Wage Growth", "real_wage_growth")
show_metric(col4, "Unemployment", "unemployment_rate", delta_color="inverse")
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
st.header("Wages vs Inflation")
st.write(
    "When wage growth is above inflation, pay is rising faster than prices and "
    "people are better off in real terms. When it's below, real incomes are falling "
    "even if wages are technically going up. The shaded gap between the two lines "
    "is real wage growth."
)

fig4 = go.Figure()

fig4.add_trace(go.Scatter(
    x=df["date"], y=df["wage_growth_rate"],
    mode="lines", name="Wage Growth (%)",
    line=dict(color="#6BCB77", width=2),
))

fig4.add_trace(go.Scatter(
    x=df["date"], y=df["cpi_inflation_rate"],
    mode="lines", name="CPI Inflation (%)",
    line=dict(color="#E8944C", width=2),
    fill="tonexty",
    fillcolor="rgba(120,120,120,0.2)",
))

fig4.update_layout(
    xaxis_title="Date",
    yaxis_title="Annual growth (%)",
    hovermode="x unified",
)

st.plotly_chart(fig4, use_container_width=True)

st.header("What's happening right now")

@st.cache_data(ttl=3600)
def get_explanation():
    from ai_explain import explain_recent_changes
    return explain_recent_changes(df)

if st.button("Generate explanation"):
    with st.spinner("Analysing the data..."):
        st.markdown(get_explanation())
    st.caption(
        "Generated by Claude from the calculated figures above. All numbers are "
        "computed in Python — the model is given finished figures and asked only "
        "to explain them, never to calculate or recall statistics."
    )
st.header("Ask a question")
st.write(
    "Ask about UK inflation, wages, unemployment or interest rates since 2015. "
    "Questions are answered by querying the underlying data — figures are computed "
    "in Python, not recalled by the AI."
)

question = st.text_input(
    "Your question",
    placeholder="e.g. When was inflation highest since 2019?",
)

if question:
    with st.spinner("Looking up the data..."):
        from ai_qa import answer_question
        st.markdown(answer_question(df, question))