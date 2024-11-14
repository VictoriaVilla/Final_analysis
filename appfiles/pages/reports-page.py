import streamlit as st
import pandas as pd
import numpy as np
from menu import menu
from pathlib import Path
import os
from streamlit_folium import st_folium, folium_static


menu()

st.title('Narre Warren South Traffic Project')
st.header('Reports')


def set_maps(i):
    st.session_state.maps = i


def set_graphs(i):
    st.session_state.graphs = i


if 'maps' not in st.session_state:
    st.session_state.maps = 0
if 'graphs' not in st.session_state:
    st.session_state.graphs = 0
if 'completed_report' not in st.session_state:
    st.session_state.completed_report = ""
if 'graphs_a' not in st.session_state:
    st.session_state.graphs_a = []

tab1, tab2 = st.tabs(
    ["Session Report", "Historical Reports"])
# change this directory to where the reports are generated
report_folder = os.path.dirname("data/reports/")


# list PDF files in the report folder
def list_pdf_files(report_folder):
    try:
        return [file for file in os.listdir(report_folder) if file.endswith('.pdf')]
    except FileNotFoundError:
        return []


# display generated reports
def display_report_content():
    st.subheader("Historical Reports")

    # check PDF reports
    pdf_files = list_pdf_files(report_folder)
    row = st.columns([0.7, 0.3], gap="small", vertical_alignment="center")

    if not pdf_files:
        st.write("No reports available.")
    else:
        for pdf in pdf_files:
            row = st.columns([0.5, 0.1, 0.4], gap="small",
                             vertical_alignment="center")
            with row[0]:
                st.write(f'{pdf}')
            with row[1]:
                report_path = report_folder + "/" + pdf
                # clickable links for each PDF
                with open(report_path, "rb") as file:
                    # download the PDF
                    st.download_button(
                        label="", icon=":material/download:", data=file, file_name=pdf)


with tab1:
    if st.session_state.completed_report == "":
        st.write("No report has been created in this session")
    else:
        with open(st.session_state.completed_report, "rb") as file:
            st.download_button(label="Download current session report", icon=":material/download:",
                               data=file, file_name=st.session_state.completed_report)
        taba, tabb = st.tabs(["Maps", "Bar Charts"])
        with taba:
            if len(st.session_state.maps_c) == 0:
                if len(st.session_state.maps_a) == 0:
                    st.write("No maps has been created")
                else:
                    c1, c2 = st.columns([0.15, 0.85])
                with c1:
                    for i in range(len(st.session_state.maps_a)):
                        st.button(
                            f"Map {st.session_state.maps_a[i][1]}", on_click=set_maps, args=[i+1])
                with c2:
                    if st.session_state.maps == 0:
                        st_folium(
                            st.session_state.maps_a[0][0], width=1000, height=800)
                    for i in range(len(st.session_state.maps_a)):
                        if st.session_state.maps == i+1:
                            if len(st.session_state.maps_a[i]) > 2:
                                st.write("Heat maps not available - Heat maps can be found in the pdf report")
                                st_folium(
                                    st.session_state.maps_a[i][0], width=1000, height=800, feature_group_to_add=st.session_state.maps_a[i][2])
                            else:
                                st_folium(
                                    st.session_state.maps_a[i][0], width=1000, height=800)
            else:
                c1, c2 = st.columns([0.15, 0.85])
                with c1:
                    for i in range(len(st.session_state.maps_c)):
                        st.button(
                            f"Map {st.session_state.maps_c[i][1]}", on_click=set_maps, args=[i+1])
                with c2:
                    if st.session_state.maps == 0:
                        st_folium(
                            st.session_state.maps_c[0][0], width=1000, height=800)
                    for i in range(len(st.session_state.maps_c)):
                        if st.session_state.maps == i+1:
                            st_folium(
                                st.session_state.maps_c[i][0], width=1000, height=800)
        with tabb:
            if len(st.session_state.graphs_c) == 0:
                if len(st.session_state.graphs_a) == 0:
                    st.write("No graphs has been created")
                else:
                    c1, c2 = st.columns([0.15, 0.85])
                    with c1:
                        for i in range(len(st.session_state.graphs_a)):
                            st.button(f"Graph {i+1}",
                                      on_click=set_graphs, args=[i+1])
                    with c2:
                        if st.session_state.graphs == 0:
                            st.html(st.session_state.graphs_a[0])
                        for i in range(len(st.session_state.graphs_a)):
                            if st.session_state.graphs == i+1:
                                st.html(st.session_state.graphs_a[i])
            else:
                c1, c2 = st.columns([0.15, 0.85])
                with c1:
                    for i in range(len(st.session_state.graphs_c)):
                        st.button(f"Graph {i+1}",
                                  on_click=set_graphs, args=[i+1])
                with c2:
                    if st.session_state.graphs == 0:
                        st.html(st.session_state.graphs_c[0])
                    for i in range(len(st.session_state.graphs_c)):
                        if st.session_state.graphs == i+1:
                            st.html(st.session_state.graphs_c[i])
with tab2:
    display_report_content()
