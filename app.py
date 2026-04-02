"""
DataWhisper - AI-Powered Data Analyst
A simplified, cleaner and more stable version.
"""

import sys
import os
sys.path.append(os.path.abspath("."))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Local utilities
from utils.data_loader import load_data, get_data_preview
from utils.schema_extractor import extract_schema, get_schema_summary_text
from utils.data_cleaner import analyze_data_quality, clean_data
from utils.visualizer import create_basic_stats_charts, display_result
from config.settings import APP_TITLE, APP_DESCRIPTION, MAX_ROWS_FOR_PREVIEW

# Choose AI Engine (Groq is default)
USE_GROQ = True

if USE_GROQ:
    from utils.groq_engine import GroqEngine as AIEngine
else:
    from utils.groq_engine import GroqEngine as AIEngine


# -----------------------------------------------------------
# Page Configuration & Styling
# -----------------------------------------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="🔮", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    h1 { color: #1f77b4; font-weight: 700; border-bottom: 3px solid #ff7f0e; padding-bottom: 6px; }
    [data-testid="stSidebar"] { background-color: #2c3e50; }
    [data-testid="stSidebar"] * { color: #ecf0f1 !important; }
    .stButton>button {
        background: linear-gradient(90deg, #1f77b4, #2ecc71);
        color: white; padding: 10px 24px; border-radius: 8px; border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #2ecc71, #1f77b4);
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------
if "df" not in st.session_state:
    st.session_state.df = None
if "schema_info" not in st.session_state:
    st.session_state.schema_info = None
if "insights" not in st.session_state:
    st.session_state.insights = None
if "ai_engine" not in st.session_state:
    try:
        st.session_state.ai_engine = AIEngine()
    except ValueError as err:
        st.error(str(err))
        st.stop()


# -----------------------------------------------------------
# Header Section
# -----------------------------------------------------------
st.markdown("""
    <div style='text-align:center;padding:20px;
         background:linear-gradient(90deg,#1f77b4,#2ecc71);
         border-radius:15px; margin-bottom:30px;'>
        <h1 style='color:white;margin:0;'>🔮 DataWhisper</h1>
        <p style='color:white;font-size:18px;margin:6px 0 0 0;'>Your AI-Powered Data Analyst</p>
    </div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------
# Sidebar – Upload Data
# -----------------------------------------------------------
with st.sidebar:
    st.markdown("## 📁 Upload Your Data")
    uploaded_file = st.file_uploader("Upload CSV or Excel", type=['csv', 'xlsx', 'xls'])

    if st.button("🎯 Use Sample Data", use_container_width=True):
        sample_path = "sample_data/sales_data.csv"
        st.session_state.df = pd.read_csv(sample_path)
        st.session_state.schema_info = extract_schema(st.session_state.df)
        from utils.auto_insights import generate_auto_insights
        st.session_state.insights = generate_auto_insights(st.session_state.df)
        st.success("Sample data loaded!")

    # Load uploaded data
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        if df is not None:
            st.session_state.df = df
            st.session_state.schema_info = extract_schema(df)
            from utils.auto_insights import generate_auto_insights
            st.session_state.insights = generate_auto_insights(df)

    # Dataset info
    if st.session_state.df is not None:
        st.markdown("---")
        st.markdown("### 📊 Dataset Info")
        col1, col2 = st.columns(2)
        col1.metric("Rows", f"{st.session_state.df.shape[0]:,}")
        col2.metric("Columns", st.session_state.df.shape[1])


# -----------------------------------------------------------
# Landing Page (Before Data Upload)
# -----------------------------------------------------------
if st.session_state.df is None:
    st.info("👈 Upload a dataset or use sample data to get started.")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.success("🤖 **AI-Powered**\n\nAsk questions in simple English.")
    with col2:
        st.warning("📊 **Smart Insights**\n\nAutomatic charts & summaries.")
    with col3:
        st.info("⚡ **Fast Results**\n\nInstant analysis and outputs.")

    st.stop()  # Stop here until user uploads data


# -----------------------------------------------------------
# When Data Is Loaded → Show Tabs
# -----------------------------------------------------------
df = st.session_state.df
schema_info = st.session_state.schema_info

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "💬 Ask Questions",
    "👀 Data Preview",
    "🧹 Clean Data",
    "📈 Quick Insights",
    "📊 Custom Charts",
    "🔍 Auto-Insights",
    "📄 Export Report"
])


# -----------------------------------------------------------
# TAB 1 – Ask Questions (AI Query)
# -----------------------------------------------------------
with tab1:
    st.subheader("🗣️ Ask a question about your data")

    user_question = st.text_input(
        "Type a question",
        placeholder="Example: What's the average revenue by region?"
    )

    if st.button("🔍 Analyze"):
        if user_question.strip():
            with st.spinner("Analyzing…"):
                schema_txt = get_schema_summary_text(schema_info)
                code = st.session_state.ai_engine.generate_pandas_code(
                    user_question, schema_txt
                )

                if code:
                    with st.expander("Generated Code"):
                        st.code(code, language='python')

                    try:
                        exec_globals = {"df": df, "pd": pd, "px": px, "go": go}
                        exec(code, exec_globals)
                        result = exec_globals.get("result", None)
                        st.markdown("### 📊 Result")
                        display_result(result)
                    except Exception as err:
                        st.error(f"Error running code: {err}")


# -----------------------------------------------------------
# TAB 2 – Data Preview
# -----------------------------------------------------------
with tab2:
    st.subheader("📋 Dataset Preview")
    st.dataframe(get_data_preview(df, MAX_ROWS_FOR_PREVIEW), use_container_width=True)


# -----------------------------------------------------------
# TAB 3 – Data Cleaning
# -----------------------------------------------------------
with tab3:
    st.subheader("🧹 Data Cleaning & Preparation")

    quality = analyze_data_quality(df)

    # Summary stats
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", f"{quality['total_rows']:,}")
    col2.metric("Columns", quality["total_columns"])
    col3.metric("Duplicates", quality["duplicate_rows"])

    # Missing values
    if quality["missing_values"]:
        st.warning("⚠️ Missing Values")
        missing_df = pd.DataFrame([
            {"Column": c, "Missing": d["count"], "Percentage": f"{d['percentage']}%"}
            for c, d in quality["missing_values"].items()
        ])
        st.dataframe(missing_df)
    else:
        st.success("No missing values detected.")

    # Cleaning Options
    st.markdown("---")
    st.markdown("### Cleaning Options")

    opts = {}

    colA, colB = st.columns(2)

    with colA:
        opts["handle_missing"] = st.checkbox("Handle Missing Values", True)
        if opts["handle_missing"]:
            opts["missing_method"] = st.selectbox(
                "Missing Value Strategy",
                ["drop", "fill_mean", "fill_median", "fill_mode"]
            )

        opts["remove_duplicates"] = st.checkbox("Remove Duplicates", True)
        opts["fix_types"] = st.checkbox("Fix Data Types", True)

    with colB:
        opts["handle_outliers"] = st.checkbox("Handle Outliers")
        if opts["handle_outliers"]:
            opts["outlier_method"] = st.selectbox("Outlier Method", ["remove", "cap"])

        opts["clean_column_names"] = st.checkbox("Clean Column Names", True)
        opts["trim_whitespace"] = st.checkbox("Trim Whitespace", True)

    if st.button("🧹 Clean Data", type="primary"):
        with st.spinner("Cleaning..."):
            cleaned_df, logs = clean_data(df, opts)

            # Update global state
            st.session_state.df = cleaned_df
            st.session_state.schema_info = extract_schema(cleaned_df)
            from utils.auto_insights import generate_auto_insights
            st.session_state.insights = generate_auto_insights(cleaned_df)

            st.success("Data cleaned successfully!")

            for msg in logs:
                st.write("•", msg)


# -----------------------------------------------------------
# TAB 4 – Quick Insights
# -----------------------------------------------------------
with tab4:
    st.subheader("📈 Quick Insights")
    create_basic_stats_charts(df)

    st.markdown("### 📊 Statistical Summary")
    st.dataframe(df.describe(), use_container_width=True)


# -----------------------------------------------------------
# TAB 5 – Custom Charts
# -----------------------------------------------------------
with tab5:
    st.subheader("📊 Build Your Custom Chart")

    num_cols = df.select_dtypes(include='number').columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    chart_type = st.selectbox("Select Chart Type", [
        "Bar Chart", "Line Chart", "Pie Chart",
        "Scatter Plot", "Box Plot", "Histogram",
        "Heatmap (Correlation)"
    ])

    # Dynamic chart builder
    if chart_type != "Heatmap (Correlation)":
        col1, col2 = st.columns(2)
        with col1:
            x = st.selectbox("X-Axis", df.columns)
        with col2:
            y = st.selectbox("Y-Axis", df.columns)

    # Plotting
    if st.button("Generate Chart"):
        try:
            if chart_type == "Bar Chart":
                fig = px.bar(df, x=x, y=y)
            elif chart_type == "Line Chart":
                fig = px.line(df, x=x, y=y)
            elif chart_type == "Pie Chart":
                fig = px.pie(df, names=x, values=y)
            elif chart_type == "Scatter Plot":
                fig = px.scatter(df, x=x, y=y)
            elif chart_type == "Box Plot":
                fig = px.box(df, x=x, y=y)
            elif chart_type == "Histogram":
                fig = px.histogram(df, x=x)
            else:
                fig = px.imshow(df.corr(), text_auto=True)

            st.plotly_chart(fig, use_container_width=True)

        except Exception as err:
            st.error(f"Error generating chart: {err}")


# -----------------------------------------------------------
# TAB 6 – Auto Insights
# -----------------------------------------------------------
with tab6:
    st.subheader("🔍 Auto-Insights")
    if st.session_state.insights:
        for item in st.session_state.insights:
            st.write("•", item)


# -----------------------------------------------------------
# TAB 7 – Export Report
# -----------------------------------------------------------
with tab7:
    st.subheader("📄 Export Report")
    st.info("Export feature coming soon.")

# Footer
st.markdown("---")
st.markdown("**Built with ❤️ by Netram | DataWhisper v2.0**")
