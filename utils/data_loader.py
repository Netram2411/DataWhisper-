"""
Handles file uploads and data loading
"""

import pandas as pd
import streamlit as st


def load_data(uploaded_file):
    """Loads data from uploaded file"""
    
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
        else:
            st.error(f"Unsupported file type: {file_extension}")
            return None
        
        if df.empty:
            st.error("The uploaded file is empty!")
            return None
        
        st.success(f"✅ Loaded {len(df)} rows and {len(df.columns)} columns")
        return df
        
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None


def get_data_preview(df, n_rows=10):
    """Returns first n rows for preview"""
    return df.head(n_rows)