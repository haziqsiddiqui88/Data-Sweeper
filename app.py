import streamlit as st
import pandas as pd
import os
from io import BytesIO
import numpy as np
import altair as alt

# Set up our App
st.set_page_config(page_title="📊Data Sweeper", page_icon="📊", layout="wide")
st.title("📊 Data Sweeper")
st.write("Transform your file between CSV and Excel formats with built-in data cleaning and visualization!")

# User Authentication
def authenticate_user():
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if username == "haziq88" and password == "giaicd":
        return True
    else:
        st.sidebar.error("Invalid username or password")
        return False

if authenticate_user():
    # File uploader with multiple file support
    uploaded_files = st.file_uploader("Upload your file (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

    # Process uploaded files
    if uploaded_files:
        for file in uploaded_files:
            file_ext = os.path.splitext(file.name)[-1].lower()  # Get file extension

            # Read file based on type
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file)
            else:
                st.error(f"Unsupported file type: {file_ext}")
                continue  # Skip invalid file

            # Display file details
            st.write(f"### File Name: {file.name}")
            st.write(f"📦 File Size: {file.getbuffer().nbytes / 1024:.2f} KB")

            # Show 5 rows of the dataframe
            st.write("🔍 *Preview of the DataFrame:*")
            st.dataframe(df.head())

            # Data Cleaning Options
            st.subheader("🧹 Data Cleaning Options")
            if st.checkbox(f"Clean Data from {file.name}"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button(f"Remove Duplicates from {file.name}"):
                        df.drop_duplicates(inplace=True)
                        st.success("✅ Duplicates Removed!")

                with col2:
                    if st.button(f"Fill Missing Values from {file.name}"):
                        numeric_cols = df.select_dtypes(include=['number']).columns
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                        st.success("✅ Missing Values Filled!")
                
                with col3:
                    if st.button(f"Normalize Data from {file.name}"):
                        numeric_cols = df.select_dtypes(include=['number']).columns
                        df[numeric_cols] = (df[numeric_cols] - df[numeric_cols].mean()) / df[numeric_cols].std()
                        st.success("✅ Data Normalized!")

                # Show cleaned data preview
                st.write("📊 *Updated DataFrame:*")
                st.dataframe(df.head())

            # Choose Specific Columns to keep or Convert to CSV/Excel
            st.subheader("Select Columns to Convert")
            columns = st.multiselect(f"Select Columns for {file.name}", df.columns, default=df.columns)
            df = df[columns]

            # Create Some Visualizations
            st.subheader("📊 Data Visualizations")
            if st.checkbox("Show Data Visualizations"):
                chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Line Chart", "Scatter Plot"])
                if chart_type == "Bar Chart":
                    st.bar_chart(df.select_dtypes(include=['number']).iloc[:, :2])
                elif chart_type == "Line Chart":
                    st.line_chart(df.select_dtypes(include=['number']).iloc[:, :2])
                elif chart_type == "Scatter Plot":
                    col_x = st.selectbox("Select X-axis Column", df.columns)
                    col_y = st.selectbox("Select Y-axis Column", df.columns)
                    scatter_chart = alt.Chart(df).mark_circle(size=60).encode(
                        x=col_x,
                        y=col_y,
                        tooltip=[col_x, col_y]
                    ).interactive()
                    st.altair_chart(scatter_chart, use_container_width=True)

            # Convert the file to CSV or Excel
            st.subheader("🔄 Convert File")

            convert_format = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=f"convert_{file.name}")

            if st.button(f"Convert {file.name}"):
                buffer = BytesIO()
                if convert_format == "CSV":
                    df.to_csv(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".csv")
                    mime_type = "text/csv"

                elif convert_format == "Excel":
                    df.to_excel(buffer, index=False, engine="openpyxl")
                    file_name = file.name.replace(file_ext, ".xlsx")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    buffer.seek(0)

                # Offer download link
                st.download_button(
                    label=f"Download {file_name} as {convert_format}",
                    data=buffer.getvalue(),
                    file_name=file_name,
                    mime=mime_type,
                )

            # Success message
            st.success("🎉 File Processing Completed!")