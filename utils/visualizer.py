"""
Handles data visualization - SMART AUTO-DETECTION (FIXED)
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import numpy as np


def create_basic_stats_charts(df):
    """
    Automatically creates appropriate charts based on data types
    """
    
    st.subheader("📊 Quick Data Overview")
    
    # Detect column types
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    # CHART 1 & 2: Numeric columns
    if len(numeric_cols) >= 1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution of first numeric column
            try:
                fig = px.histogram(
                    df, 
                    x=numeric_cols[0],
                    title=f'Distribution of {numeric_cols[0]}',
                    color_discrete_sequence=['#1f77b4']
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create histogram: {str(e)}")
        
        with col2:
            # Box plot - SAFE VERSION
            if len(numeric_cols) >= 1:
                try:
                    # Take up to 3 numeric columns
                    cols_to_plot = numeric_cols[:min(3, len(numeric_cols))]
                    
                    # Create individual box plots
                    fig = go.Figure()
                    
                    for col in cols_to_plot:
                        fig.add_trace(go.Box(
                            y=df[col].dropna(),
                            name=col,
                            boxmean='sd'
                        ))
                    
                    fig.update_layout(
                        title='Numeric Columns Overview',
                        showlegend=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not create box plot: {str(e)}")
    
    # CHART 3: Categorical + Numeric
    if numeric_cols and categorical_cols:
        col1, col2 = st.columns(2)
        
        with col1:
            try:
                cat_col = categorical_cols[0]
                num_col = numeric_cols[0]
                
                # Limit to top 10 categories
                top_categories = df[cat_col].value_counts().head(10).index
                filtered_df = df[df[cat_col].isin(top_categories)]
                
                agg_data = filtered_df.groupby(cat_col)[num_col].sum().reset_index()
                
                fig = px.bar(
                    agg_data,
                    x=cat_col,
                    y=num_col,
                    title=f'{num_col} by {cat_col}',
                    color=num_col,
                    color_continuous_scale='Blues'
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create bar chart: {str(e)}")
        
        with col2:
            try:
                # Pie chart
                cat_counts = df[cat_col].value_counts().head(8)
                
                fig = px.pie(
                    values=cat_counts.values,
                    names=cat_counts.index,
                    title=f'Distribution of {cat_col}'
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create pie chart: {str(e)}")
    
    # CHART 4: Correlation heatmap
    if len(numeric_cols) >= 2:
        try:
            st.subheader("🔥 Correlation Heatmap")
            
            # Take up to 5 numeric columns
            cols_for_corr = numeric_cols[:min(5, len(numeric_cols))]
            corr_matrix = df[cols_for_corr].corr()
            
            fig = px.imshow(
                corr_matrix,
                text_auto='.2f',
                aspect='auto',
                title='Correlation Between Numeric Variables',
                color_continuous_scale='RdBu_r',
                zmin=-1,
                zmax=1
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not create correlation heatmap: {str(e)}")
    
    # Info about charts
    with st.expander("ℹ️ About These Charts"):
        st.markdown(f"""
        **Charts automatically generated based on your data:**
        
        - **Numeric columns:** {len(numeric_cols)} ({', '.join(numeric_cols[:5]) if numeric_cols else 'None'})
        - **Categorical columns:** {len(categorical_cols)} ({', '.join(categorical_cols[:3]) if categorical_cols else 'None'})
        
        Charts adapt automatically to your dataset!
        """)


def display_result(result):
    """
    Intelligently displays any type of result
    """
    
    if result is None:
        st.warning("No result generated")
        return
    
    if hasattr(result, 'show'):
        st.plotly_chart(result, use_container_width=True)
    elif isinstance(result, pd.DataFrame):
        st.dataframe(result, use_container_width=True)
    elif isinstance(result, pd.Series):
        st.dataframe(result.to_frame(), use_container_width=True)
    else:
        if isinstance(result, (int, float)):
            st.metric("Result", f"{result:,.2f}" if isinstance(result, float) else f"{result:,}")
        else:
            st.write(result)