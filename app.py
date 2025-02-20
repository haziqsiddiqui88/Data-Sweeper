# Import necessary libraries
import streamlit as st
import pandas as pd
import os 
from io import BytesIO

# Set up our App
st.set_page_config(page_title="📊Data Sweeper", page_icon="📊", layout="wide")
st.title("📊 Data Sweeper")
st.write("Transform your file between CSV and Excel formats with built-in data cleaning and visualization!")

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
        st.write("🔍 **Preview of the DataFrame:**")
        st.dataframe(df.head())

        # Data Cleaning Options
        st.subheader("🧹 Data Cleaning Options")
        if st.checkbox(f"Clean Data from {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.success("✅ Duplicates Removed!")

            with col2:
                if st.button(f"Fill Missing Values from {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.success("✅ Missing Values Filled!")

            # Show cleaned data preview
            st.write("📊 **Updated DataFrame:**")
            st.dataframe(df.head())

        # Choose Specific Columns to keep or Convert to CSV/Excel
        st.subheader("Select Columns to Convert")
        columns = st.multiselect(f"Select Columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]

        # Create Some Visualizations
        st.subheader("📊 Data Visualizations")
        if st.checkbox("Show Data Visualizations"):
            st.bar_chart(df.select_dtypes(include=['number']).iloc[:,:2])

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
