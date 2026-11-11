"""
Streamlit dashboard entry point for Cellular Device Performance Lab.
Phase 1: basic data generation and exploration.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from src.data_generator.generator import SyntheticDataGenerator
from src.validation.validator import validate_dataframe

st.set_page_config(page_title="Cellular Device Performance Lab", layout="wide")
st.title("Cellular Device Performance Lab")
st.caption("Synthetic data only — for interview preparation and engineering simulation. Not real device measurements.")

scenario = st.sidebar.selectbox(
    "Scenario",
    ["baseline_lte", "degraded_sinr", "high_mobility", "ul_degradation"],
)
seed = st.sidebar.number_input("Random seed", value=42, min_value=0)

if st.sidebar.button("Generate Dataset"):
    with st.spinner("Generating synthetic trace..."):
        gen = SyntheticDataGenerator(seed=int(seed))
        df = gen.generate(scenario)
        validated, warnings, quality = validate_dataframe(df)
        st.session_state["df"] = df
        st.session_state["quality"] = quality
        st.session_state["warnings"] = warnings

if "df" in st.session_state:
    df = st.session_state["df"]
    st.metric("Data Quality Score", st.session_state["quality"])
    if st.session_state["warnings"]:
        st.warning("\n".join(st.session_state["warnings"]))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg RSRP (dBm)", f"{df['rsrp_dbm'].mean():.1f}")
    col2.metric("Avg SINR (dB)", f"{df['sinr_db'].mean():.1f}")
    col3.metric("Avg DL Throughput (Mbps)", f"{df['dl_throughput_mbps'].mean():.1f}")
    col4.metric("Avg RTT (ms)", f"{df['rtt_ms'].mean():.1f}")

    st.subheader("Time Series (sample)")
    st.line_chart(df.set_index("timestamp")[["rsrp_dbm", "sinr_db", "dl_throughput_mbps"]].head(200))

    st.subheader("Raw Data Preview")
    st.dataframe(df.head(20))
else:
    st.info("Select a scenario and click **Generate Dataset** to begin.")
