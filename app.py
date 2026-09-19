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