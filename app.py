
import streamlit as st
import pandas as pd
import tempfile
import os

# Fixed parameters to extract
target_params = [
    "Hole Depth (feet)",
    "Bit Depth (feet)",
    "Hook Load (klbs)",
    "Total Mud Volume (barrels)",
    "Weight on Bit (klbs)",
    "SHAKER #1 (Units)",
    "Tool Face (degrees)",
    "SHAKER #2 (Units)",
    "SHAKER #3 (PERCENT)",
    "Heavy Ratio (percent)",
    "PVT Monitor Mud Gain/Loss (barrels)",
    "Total Mud Low Warning (barrels)",
    "Flow Low Warning (flow_percent)",
    "Flow High Warning (flow_percent)",
    "Trip Mud High Warning (barrels)",
    "MA_Temp (degF)",
    "MA_Flow_Rate (gal/min)",
    "Site Mud Volume (barrels)",
    "Inactive Mud Volume (barrels)"
]

st.title("CSV Parameter Extractor (Optimized for Render)")
st.markdown("Upload a large CSV file. This app extracts predefined drilling parameters and provides a downloadable CSV. Optimized for Render hosting.")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file:
    with st.spinner("Processing, please wait..."):
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
            temp_file.write(uploaded_file.read())
            temp_file.close()

            df = pd.read_csv(temp_file.name, header=None, usecols=range(26), nrows=150)
            time_labels = df.iloc[0, 1:]
            data_df = df.set_index(0).iloc[1:]
            filtered = data_df.loc[data_df.index.intersection(target_params)]
            filtered.columns = time_labels
            transposed = filtered.T
            transposed.index.name = "Timestamp"
            final_df = transposed.sort_index()

            csv = final_df.to_csv(index=True).encode('utf-8')
            st.success("File processed successfully!")
            st.download_button(
                label="Download Filtered CSV",
                data=csv,
                file_name="Filtered_Parameters.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            os.remove(temp_file.name)
