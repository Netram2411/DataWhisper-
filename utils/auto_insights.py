"""
Automatically generates insights from data
"""

import pandas as pd
import streamlit as st


def generate_auto_insights(df):
    """
    Analyzes DataFrame and returns key insights automatically
    
    Args:
        df: pandas DataFrame
        
    Returns:
        List of insight strings
    """
    insights = []
    
    try:
        # 1. Dataset overview
        insights.append(f"📊 Dataset contains {len(df):,} rows and {len(df.columns)} columns")
        
        # 2. Numeric columns insights
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if numeric_cols:
            insights.append(f"📈 Found {len(numeric_cols)} numeric columns: {', '.join(numeric_cols[:5])}")
            
            for col in numeric_cols[:3]:  # First 3 numeric columns
                try:
                    max_val = df[col].max()
                    min_val = df[col].min()
                    avg_val = df[col].mean()
                    
                    insights.append(f"• {col}: Range {min_val:,.2f} to {max_val:,.2f}, Average: {avg_val:,.2f}")
                except:
                    insights.append(f"• {col}: Unable to calculate statistics")
        else:
            insights.append("ℹ️ No numeric columns found")
        
        # 3. Categorical columns insights
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if categorical_cols:
            insights.append(f"🏷️ Found {len(categorical_cols)} text columns: {', '.join(categorical_cols[:5])}")
            
            for col in categorical_cols[:2]:  # First 2 categorical columns
                try:
                    unique_count = df[col].nunique()
                    most_common = df[col].mode()[0] if len(df[col].mode()) > 0 else "N/A"
                    
                    insights.append(f"• {col}: {unique_count} unique values, Most common: {most_common}")
                except:
                    insights.append(f"• {col}: Unable to analyze")
        else:
            insights.append("ℹ️ No text columns found")
        
        # 4. Top performers (flexible - looks for any numeric column)
        if numeric_cols and categorical_cols:
            try:
                # Use first numeric and first categorical column
                numeric_col = numeric_cols[0]
                categorical_col = categorical_cols[0]
                
                top_group = df.groupby(categorical_col)[numeric_col].sum().idxmax()
                top_value = df.groupby(categorical_col)[numeric_col].sum().max()
                
                insights.append(f"🏆 Top {categorical_col} by {numeric_col}: {top_group} ({top_value:,.2f})")
            except:
                pass  # Skip if grouping fails
        
        # 5. Missing data detection
        missing_cols = df.columns[df.isnull().any()].tolist()
        if missing_cols:
            total_missing = df.isnull().sum().sum()
            insights.append(f"⚠️ Found {total_missing:,} missing values in {len(missing_cols)} columns")
            insights.append(f"   Columns with missing data: {', '.join(missing_cols[:5])}")
        else:
            insights.append("✅ No missing data detected")
        
        # 6. Duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            insights.append(f"⚠️ Found {duplicates:,} duplicate rows")
        else:
            insights.append("✅ No duplicate rows found")
        
        # 7. Date columns (if any)
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        if date_cols:
            for date_col in date_cols[:1]:  # First date column only
                try:
                    min_date = df[date_col].min()
                    max_date = df[date_col].max()
                    date_range = (max_date - min_date).days
                    insights.append(f"📅 {date_col}: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')} ({date_range} days)")
                except:
                    pass
        
        # 8. Data types summary
        dtype_counts = df.dtypes.value_counts()
        dtype_summary = ", ".join([f"{count} {dtype}" for dtype, count in dtype_counts.items()])
        insights.append(f"📋 Column types: {dtype_summary}")
        
    except Exception as e:
        insights.append(f"❌ Error generating insights: {str(e)}")
    
    return insights


def display_auto_insights(insights):
    """
    Displays insights in a nice format
    
    Args:
        insights: List of insight strings
    """
    st.subheader("🔍 Auto-Generated Insights")
    
    if not insights or insights is None:
        st.warning("No insights generated. Please upload data first.")
        return
    
    for insight in insights:
        st.markdown(f"{insight}")