"""
Automatic Data Cleaning Utilities
"""

import pandas as pd
import numpy as np
import streamlit as st



def analyze_data_quality(df):
    """
    Analyzes dataset and identifies issues
    
    Returns:
        Dictionary with quality metrics
    """
    
    quality_report = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_values": {},
        "duplicate_rows": df.duplicated().sum(),
        "data_type_issues": [],
        "outliers": {}
    }
    
    # Check missing values per column
    for col in df.columns:
        missing = df[col].isnull().sum()
        if missing > 0:
            quality_report["missing_values"][col] = {
                "count": int(missing),
                "percentage": round((missing / len(df)) * 100, 2)
            }
    
    # Check for numeric columns stored as strings
    for col in df.columns:
        if df[col].dtype == 'object':
            # Try to convert to numeric
            try:
                pd.to_numeric(df[col], errors='raise')
                quality_report["data_type_issues"].append(f"{col} appears numeric but stored as text")
            except:
                pass
    
    # Detect outliers in numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        
        if len(outliers) > 0:
            quality_report["outliers"][col] = {
                "count": len(outliers),
                "percentage": round((len(outliers) / len(df)) * 100, 2)
            }
    
    return quality_report


def clean_data(df, options):
    """
    Cleans data based on selected options
    
    Args:
        df: DataFrame to clean
        options: Dictionary of cleaning options
        
    Returns:
        Cleaned DataFrame and cleaning log
    """
    
    cleaned_df = df.copy()
    cleaning_log = []
    
    # 1. Handle Missing Values
    if options.get("handle_missing"):
        method = options.get("missing_method", "drop")
        
        if method == "drop":
            before = len(cleaned_df)
            cleaned_df = cleaned_df.dropna()
            removed = before - len(cleaned_df)
            cleaning_log.append(f"✓ Removed {removed} rows with missing values")
        
        elif method == "fill_mean":
            numeric_cols = cleaned_df.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                if cleaned_df[col].isnull().any():
                    mean_val = cleaned_df[col].mean()
                    cleaned_df[col].fillna(mean_val, inplace=True)
                    cleaning_log.append(f"✓ Filled missing values in {col} with mean ({mean_val:.2f})")
        
        elif method == "fill_median":
            numeric_cols = cleaned_df.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                if cleaned_df[col].isnull().any():
                    median_val = cleaned_df[col].median()
                    cleaned_df[col].fillna(median_val, inplace=True)
                    cleaning_log.append(f"✓ Filled missing values in {col} with median ({median_val:.2f})")
        
        elif method == "fill_mode":
            for col in cleaned_df.columns:
                if cleaned_df[col].isnull().any():
                    mode_val = cleaned_df[col].mode()[0]
                    cleaned_df[col].fillna(mode_val, inplace=True)
                    cleaning_log.append(f"✓ Filled missing values in {col} with mode ({mode_val})")
    
    # 2. Remove Duplicates
    if options.get("remove_duplicates"):
        before = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates()
        removed = before - len(cleaned_df)
        if removed > 0:
            cleaning_log.append(f"✓ Removed {removed} duplicate rows")
    
    # 3. Fix Data Types
    if options.get("fix_types"):
        for col in cleaned_df.columns:
            if cleaned_df[col].dtype == 'object':
                # Try numeric conversion
                try:
                    cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='raise')
                    cleaning_log.append(f"✓ Converted {col} from text to numeric")
                except:
                    # Try date conversion
                    try:
                        cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='raise')
                        cleaning_log.append(f"✓ Converted {col} to datetime")
                    except:
                        pass
    
    # 4. Handle Outliers
    if options.get("handle_outliers"):
        method = options.get("outlier_method", "remove")
        numeric_cols = cleaned_df.select_dtypes(include=['number']).columns
        
        for col in numeric_cols:
            Q1 = cleaned_df[col].quantile(0.25)
            Q3 = cleaned_df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            if method == "remove":
                before = len(cleaned_df)
                cleaned_df = cleaned_df[(cleaned_df[col] >= lower_bound) & (cleaned_df[col] <= upper_bound)]
                removed = before - len(cleaned_df)
                if removed > 0:
                    cleaning_log.append(f"✓ Removed {removed} outliers from {col}")
            
            elif method == "cap":
                capped = 0
                capped += (cleaned_df[col] < lower_bound).sum()
                capped += (cleaned_df[col] > upper_bound).sum()
                
                cleaned_df[col] = cleaned_df[col].clip(lower_bound, upper_bound)
                if capped > 0:
                    cleaning_log.append(f"✓ Capped {capped} outliers in {col}")
    
    # 5. Clean Column Names
    if options.get("clean_column_names"):
        old_names = cleaned_df.columns.tolist()
        new_names = []
        
        for col in old_names:
            # Lowercase, remove spaces, special chars
            new_name = col.lower().strip()
            new_name = new_name.replace(' ', '_')
            new_name = ''.join(c for c in new_name if c.isalnum() or c == '_')
            new_names.append(new_name)
        
        cleaned_df.columns = new_names
        cleaning_log.append(f"✓ Cleaned all column names (lowercase, underscores)")
    
    # 6. Trim Whitespace in Text Columns
    if options.get("trim_whitespace"):
        text_cols = cleaned_df.select_dtypes(include=['object']).columns
        for col in text_cols:
            cleaned_df[col] = cleaned_df[col].str.strip()
        if len(text_cols) > 0:
            cleaning_log.append(f"✓ Trimmed whitespace in {len(text_cols)} text columns")
    
    return cleaned_df, cleaning_log