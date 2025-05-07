import streamlit as st
import pandas as pd

# Title
st.title("Data Warehousing & Enterprise Data Management")

# File Upload
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.write(f"Loaded {df.shape[0]} rows and {df.shape[1]} columns")

    # Sidebar filters
    column_selection = st.sidebar.selectbox("Select a column to filter", df.columns)
    unique_values = df[column_selection].unique()
    selected_value = st.sidebar.selectbox("Filter by", unique_values)

    # Filtered Data
    filtered_df = df[df[column_selection] == selected_value]

    # Layout organization
    tab1, tab2 = st.tabs(["Raw Data", "Filtered Data"])
    with tab1:
        st.dataframe(df)
    with tab2:
        st.dataframe(filtered_df)

    # Toggle sections with expander
    with st.expander("View Data Summary"):
        st.write(df.describe())

    with st.expander("View Metadata"):
        st.write("Data Warehousing involves structuring data efficiently for querying and analysis.")
        st.write("Enterprise Data Management focuses on ensuring data accuracy and accessibility.")