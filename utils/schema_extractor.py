"""
Extracts schema and sample data from uploaded files
"""

import pandas as pd
import numpy as np
from config.settings import MAX_SCHEMA_ROWS


def extract_schema(df):
    """Extract minimal schema information to send to AI"""
    
    schema_info = {
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "shape": df.shape,
        "sample_rows": df.head(MAX_SCHEMA_ROWS).to_dict('records'),
        "basic_stats": {}
    }
    
    # Add basic statistics for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        schema_info["basic_stats"][col] = {
            "min": float(df[col].min()),
            "max": float(df[col].max()),
            "mean": float(df[col].mean()),
            "median": float(df[col].median())
        }
    
    return schema_info


def get_schema_summary_text(schema_info):
    """Converts schema info into text for AI"""
    
    summary = f"""
Dataset Information:
- Total Rows: {schema_info['shape'][0]}
- Total Columns: {schema_info['shape'][1]}

Columns and Types:
"""
    
    for col, dtype in schema_info['dtypes'].items():
        summary += f"- {col}: {dtype}\n"
    
    if schema_info['basic_stats']:
        summary += "\nNumeric Column Statistics:\n"
        for col, stats in schema_info['basic_stats'].items():
            summary += f"- {col}: min={stats['min']:.2f}, max={stats['max']:.2f}, mean={stats['mean']:.2f}\n"
    
    summary += f"\nSample Data (first {MAX_SCHEMA_ROWS} rows):\n"
    summary += str(schema_info['sample_rows'])
    
    return summary