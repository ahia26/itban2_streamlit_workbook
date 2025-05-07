import streamlit as st
import pandas as pd

# Title
st.title("CSV File Explorer")

# Upload CSV file
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

# Load and process data if a file is uploaded
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Check if the file has at least 5 columns
    if len(df.columns) < 5:
        st.error("The file must have at least 5 columns.")
    else:
        # Show raw data checkbox
        if st.checkbox("Show raw data"):
            st.dataframe(df)

        # Selectbox to filter by a column
        column_to_filter = st.selectbox("Select a column to filter", df.columns)
        unique_values = df[column_to_filter].unique()
        selected_value = st.selectbox(f"Select a value in {column_to_filter}", unique_values)

        # Display filtered results
        filtered_df = df[df[column_to_filter] == selected_value]
        st.dataframe(filtered_df)