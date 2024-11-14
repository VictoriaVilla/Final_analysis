import base64
import contextlib
import streamlit as st
from menu import menu
import os
import pandas as pd
import io
from file_analysis import run_analysis as run_analysis1
from file_analysis2 import run_analysis as run_analysis2

menu()


def list_files(folder_path):
    try:
        files = os.listdir(folder_path)
        return [f for f in files if f.endswith('.csv')]
    except FileNotFoundError:
        return []


def load_data(file_path, files):
    csv_files = [pd.read_csv(file_path+'/'+f) for f in files]
    try:
        df = pd.concat(csv_files, ignore_index=True)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        df = None
    return df


def get_date_range(df, start_column, end_column):
    try:
        min_start_date = pd.to_datetime(df[start_column]).min().date()
        max_end_date = pd.to_datetime(df[end_column]).max().date()
        return min_start_date, max_end_date
    except Exception as e:
        st.error(f"Error extracting date range: {e}")
        return None, None


def set_state_vendor(i, vendor):
    st.session_state.stage_a = i
    st.session_state.vendor_selected = vendor
    if (not vendor):
        st.session_state.completed_report = ""
        st.session_state.maps_c = []
        st.session_state.graphs_c = []
        st.session_state.maps_a = []
        st.session_state.graphs_a = []


def set_stage_a(i):
    st.session_state.stage_a = i


def options_select(options):
    if "selected_options" in st.session_state:
        if "All" in st.session_state["selected_options"]:
            st.session_state["selected_options"] = [options[0]]
            st.session_state["max_selections"] = 1
        else:
            st.session_state["max_selections"] = len(options)


st.title('Narre Warren South Traffic Project', anchor=False)
st.header('Analysis', anchor=False)

# Define paths for AeroRanger and CompassIoT folders
path = os.path.dirname("data/files/")
aero_ranger_folder = os.path.join(path, "AeroRanger")
compass_iot_folder = os.path.join(path, "CompassIoT")

# List files in both folders
f_a = list_files(aero_ranger_folder)
f_c = list_files(compass_iot_folder)

# Store files in session state
if 'files_a' not in st.session_state:
    st.session_state.files_a = f_a

if 'files_c' not in st.session_state:
    st.session_state.files_c = f_c

if 'maps_c'not in st.session_state:
    st.session_state.maps_c = []

if 'graphs_c' not in st.session_state:
    st.session_state.graphs_c = []

if 'completed_report' not in st.session_state:
    st.session_state.completed_report = ""

file_options_c = st.session_state.files_c
if "All" not in file_options_c:
    file_options_c.insert(0, "All")

if "max_selections" not in st.session_state:
    st.session_state["max_selections"] = len(file_options_c)

# Ensure files are uploaded before proceeding
if ('files_a' and 'files_c' not in st.session_state) or (not st.session_state['files_c'] and not st.session_state['files_a']):
    st.write("No files uploaded. Please upload files on the Files page.")
    st.page_link("pages\\files-page.py", label="Files",
                 icon=":material/folder_open:")
else:
    # Vendor selection stage
    if 'vendor_selected' not in st.session_state:
        st.session_state.vendor_selected = False

    if 'stage_a' not in st.session_state:
        st.session_state.stage_a = 0

    if st.session_state.stage_a == 0:
        if not st.session_state.vendor_selected:
            st.write("Choose the vendor")
            col1, col2 = st.columns(2)

            with col1:
                st.button("Compass IOT", on_click=set_state_vendor,
                          args=[1, "Compass IOT"], type="primary", disabled=(not st.session_state.files_c))

            with col2:
                st.button("AeroRanger", on_click=set_state_vendor,
                          args=[1, "AeroRanger"], type="primary", disabled=(not st.session_state.files_a))

    # When Compass IOT is selected, allow date range and file selection
    if st.session_state.stage_a == 1:

        if st.session_state.vendor_selected == "Compass IOT":
            st.subheader("Compass IOT")
            st.write("Select the file")

            # File selection
            files = st.session_state.files_c
            st.multiselect(
                label="Select an file",
                options=file_options_c,
                key="selected_options",
                max_selections=st.session_state["max_selections"],
                on_change=options_select,
                args=[files],
            )

            if len(st.session_state["selected_options"]) >= 1:
                if "All" in st.session_state["selected_options"]:
                    files.remove("All")
                    df = load_data(compass_iot_folder, files)
                else:
                    # Load selected file to get date range
                    df = load_data(compass_iot_folder,
                                   st.session_state["selected_options"])

                if df is not None:
                    min_start_date, max_end_date = get_date_range(
                        df, 'StartDate', 'EndDate')

                    if min_start_date and max_end_date:
                        st.write(
                            f"Date range in file: {min_start_date} to {max_end_date}")

                        # Allow user to select either the whole date range or a specific range within it
                        date_range_option = st.radio(
                            "Select Date Range",
                            ("Whole Date Range", "Specific Date Range"), index=None
                        )

                        if date_range_option == "Whole Date Range":
                            start_date = min_start_date
                            end_date = max_end_date
                            st.write(
                                f"Selected Date Range: {start_date} to {end_date}")

                        elif date_range_option == "Specific Date Range":
                            col_start, col_end = st.columns(2)

                            with col_start:
                                start_date = st.date_input(
                                    "Start Date", value=min_start_date, min_value=min_start_date, max_value=max_end_date)

                            with col_end:
                                end_date = st.date_input(
                                    "End Date", value=max_end_date, min_value=min_start_date, max_value=max_end_date)
                        if date_range_option is not None:
                            col1, col2 = st.columns([0.1, 0.9])

                            with col1:
                                st.button(
                                    "Back", on_click=set_state_vendor, args=[0, False])

                            with col2:
                                if st.button("Start Analysis", type="primary"):
                                    if start_date and end_date:
                                        if (len(st.session_state["selected_options"]) == 1):
                                            st.write(
                                                f"Analysis started for {st.session_state.selected_options[0]}, from {start_date} to {end_date}")
                                        else:
                                            st.write(
                                                f"Analysis started for files: {st.session_state.selected_options}, from {start_date} to {end_date}")
                                        with st.spinner("Running analysis..."):
                                            if (st.session_state.selected_options[0] == "All"):
                                                pdf_path = run_analysis1(files, "app", start_date, end_date, "")
                                            else:
                                                pdf_path = run_analysis1(
                                                    st.session_state.selected_options, "app", start_date, end_date, "")
                                        if pdf_path:  # If PDF was created successfully
                                            st.success("Analysis completed.")
                                            st.toast(
                                                "Analysis completed.", icon='🎉')
                                            st.session_state.completed_report = pdf_path
                                            set_stage_a(2)
                                            st.switch_page(
                                                "pages\\reports-page.py")
                                        else:
                                            st.error("Analysis failed.")
                                    else:
                                        st.write(
                                            "Please select a valid date range")

        if st.session_state.vendor_selected == "AeroRanger":
            st.subheader("AeroRanger")

            st.write("Select a file")
            file_options = st.session_state.files_a
            selected_file = st.selectbox("Choose file", file_options)

            col1, col2 = st.columns(2)

            with col1:
                st.button("Back", on_click=set_state_vendor, args=[0, False])

            with col2:
                if st.button("Start Analysis", type="primary"):
                    st.write(f"Analysis started for file: {selected_file}")
                    if selected_file:
                        # Create a buffer to capture the output
                        output_buffer = io.StringIO()

                        # Redirect stdout to the buffer
                        with contextlib.redirect_stdout(output_buffer):
                            with st.spinner("Running analysis..."):
                                pdf_path = run_analysis2(selected_file, "app", "")
                        if pdf_path:  # If PDF was created successfully
                            st.success("Analysis completed.")
                            st.toast("Analysis completed.", icon='🎉')
                            st.session_state.completed_report = pdf_path
                            set_stage_a(2)
                            st.switch_page("pages\\reports-page.py")

    if st.session_state.stage_a == 2:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Go to Report"):
                st.switch_page("pages\\reports-page.py")
        with col2:
            st.button("Create new report",
                      on_click=set_state_vendor, args=[0, False])
            st.write("Creating a new report will delete last created report from the session")
            st.write("To access deleted reports from session, go to Historical Reports in the Reports section")
