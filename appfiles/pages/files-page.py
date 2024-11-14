import os
import streamlit as st
from menu import menu


def set_state(i):
    st.session_state.stage_f = i


def list_files(folder_path):
    try:
        files = os.listdir(folder_path)
        return [f for f in files if f.endswith('.csv')]
    except FileNotFoundError:
        return []


st.set_page_config(layout="centered")

menu()

st.title('Narre Warren South Traffic Project')
st.header('Files')

if 'stage_f' not in st.session_state:
    st.session_state.stage_f = 0
if 'files_a' not in st.session_state:
    st.session_state.files_a = False
if 'files_c' not in st.session_state:
    st.session_state.files_c = False

path = os.path.dirname("data/files/")
aero_ranger_folder = os.path.join(path, "AeroRanger")
compass_iot_folder = os.path.join(path, "CompassIoT")

st.write("Existing CSV Files in: ")

selected_files = []

col1, col2 = st.columns(2)
with col1:
    st.subheader("**AeroRanger Folder:**")
    aero_files = list_files(aero_ranger_folder)
    if aero_files:
        st.session_state.files_a = aero_files
        for file in aero_files:
            st.write(file)
    else:
        st.write("No CSV files found.")

with col2:
    st.subheader("**CompassIoT Folder:**")
    compass_files = list_files(compass_iot_folder)
    if compass_files:
        st.session_state.files_c = compass_files
        for file in compass_files:
            st.write(file)
    else:
        st.write("No CSV files found.")

if compass_files or aero_files:
    if st.button("Go to Analysis"):
        st.switch_page("pages\\analysis-page.py")

# where user uploads
st.subheader("Upload CSV Files")
if st.session_state.stage_f >= 0:
    folder_choice = st.radio("Select the folder to upload into:", (
        "AeroRanger", "CompassIoT"), on_change=set_state, args=[1], index=None)

if st.session_state.stage_f == 1:
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        if folder_choice == "AeroRanger":
            save_path = os.path.join(aero_ranger_folder, uploaded_file.name)
        else:
            save_path = os.path.join(compass_iot_folder, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File uploaded successfully to {folder_choice} folder.")
        st.button("Refresh", icon=":material/refresh:",
                  on_click=set_state, args=[0])
