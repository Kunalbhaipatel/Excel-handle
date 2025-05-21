import streamlit as st
import pandas as pd
import os
import requests

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

st.title("XLSB Parameter Extractor (Large File Compatible)")
st.markdown("Upload a .xlsb file, paste a local file path, or provide a public link to a .xlsb file. This app extracts predefined drilling parameters and allows CSV download.")

method = st.radio("Choose data source method:", ["Upload File", "Paste Local Path", "Paste Public URL"])

df = None

if method == "Upload File":
    uploaded_file = st.file_uploader("Choose an XLSB file", type=["xlsb"])
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, engine="pyxlsb", header=None, usecols="A:Z", nrows=150)
        except Exception as e:
            st.error(f"Error reading uploaded file: {str(e)}")

elif method == "Paste Local Path":
    file_path = st.text_input("Enter full path to the XLSB file (e.g. /mnt/data/filename.xlsb):")
    if file_path and os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path, engine="pyxlsb", header=None, usecols="A:Z", nrows=150)
        except Exception as e:
            st.error(f"Error reading local file: {str(e)}")
    elif file_path:
        st.warning("The file path does not exist or is not accessible.")

elif method == "Paste Public URL":
    url = st.text_input("Enter public URL to the XLSB file:")
    if url:
        try:
            r = requests.get(url)
            r.raise_for_status()
            with open("temp_download.xlsb", "wb") as f:
                f.write(r.content)
            df = pd.read_excel("temp_download.xlsb", engine="pyxlsb", header=None, usecols="A:Z", nrows=150)
            os.remove("temp_download.xlsb")
        except Exception as e:
            st.error(f"Error reading file from URL: {str(e)}")

if df is not None:
    try:
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
        st.error(f"Processing error: {str(e)}")
