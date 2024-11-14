import datetime
from utilities import utilities as ut
from utilities import utilities2 as ut2
from analysis import analysis2 as a2
from visualization import visualization2 as v2
from PyQt5.QtWidgets import QApplication
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reporting import textfilecreator as tfc
import pandas as pd
import streamlit as st


def run_analysis(selected_file, interface, app):
    path = "data/files/AeroRanger/"
    print("AeroRanger analysis started\nCompiling files...")
    if interface == "app":
        st.write("Compass IoT analysis started")
        st.write("Compiling files...")
        df = pd.read_csv(path+selected_file)
    else:
        df = ut.read_csv_files(path)
    if (df is None):
        print("Compiling files failed - analysis cancelled")
        if interface == "app":
            st.write("Compiling files failed - analysis cancelled")
    else:
        print("Files compiled.")
        if interface == "app":
            st.write("Files compiled.")
            st.write("File contains " + str(df.shape[0]) + " rows")
            st.write("Filtering data files...")
        print("File contains " + str(df.shape[0]) + " rows")
        print("Filtering data files...")
        good_df, bad_df = ut2.filter_data(df)
        if good_df is None:
            if interface == "app":
                st.write("Filtering failed - analysis cancelled")
            print("Filtering failed - analysis cancelled")
        else:
            print("Data filtered.")

            print("Starting the analysis...")
            if interface == "app":
                st.write("Data filtered.")
                st.write("Starting the analysis...")
            long_stay = a2.long_stay(good_df)
            no_parking = a2.parking_in_no_parking(good_df)
            print("Analysis finished.")
            if interface == "app":
                st.write("Analysis finished.")

            ct = datetime.datetime.now()
            sample_style_sheet = getSampleStyleSheet()
            elements = []
            file_name = 'data/reports/AeroRanger-report' + \
                ct.strftime("%d-%m-%Y-%H-%M") + '.pdf'
            file = SimpleDocTemplate(file_name, pagesize=letter)
            elements.append(Paragraph("Findings of the analysis of Compass IOT data.",
                                      sample_style_sheet['Heading1']))
            elements.append(Paragraph(str(bad_df.shape[0]) + " rows were filtered out, leaving "
                                      + str(good_df.shape[0]) +
                                      " rows for analysis",
                                      sample_style_sheet['BodyText']))
            elements.append(Paragraph("This represents the " + str(round((bad_df.shape[0]*100)/df.shape[0], 2)) + "% of the total data.",
                                      sample_style_sheet['BodyText']))

            elements.append(Paragraph(" ", sample_style_sheet['Heading1']))
            values = [[Paragraph("Long stay infractions", sample_style_sheet['Heading2']), ""],
                      [Paragraph("Number of infractions", sample_style_sheet['BodyText']),
                       Paragraph(str(long_stay.shape[0])+" Cars", sample_style_sheet['BodyText'])],
                      [Paragraph("Min time of stay", sample_style_sheet['BodyText']),
                       Paragraph(str((long_stay['duration_hours']).min())+" Hours", sample_style_sheet['BodyText'])],
                      [Paragraph("Max time of stay", sample_style_sheet['BodyText']),
                       Paragraph(str((long_stay['duration_hours']).max())+" Hours", sample_style_sheet['BodyText'])],]
            elements.append(tfc.toTable(values))
            elements.append(Paragraph(" ", sample_style_sheet['Heading1']))

            values = [[Paragraph("Parking in no parking infractions", sample_style_sheet['Heading2']), ""],
                      [Paragraph("Number of infractions", sample_style_sheet['BodyText']),
                       Paragraph(str(no_parking.shape[0])+" Cars", sample_style_sheet['BodyText'])],]
            elements.append(tfc.toTable(values))
            elements.append(Paragraph(" ", sample_style_sheet['Heading1']))

            file.build(elements)

            l_stay = v2.plot_long_stay_points(
                long_stay, "Long Stay infractions", file_name)
            p_in_no_p = v2.plot_Heatmap(
                no_parking, "Parking in no parking area", file_name)
            if (interface == "app"):
                st.write("Maps and Plots created.")
                st.session_state.maps_a = [l_stay[1], p_in_no_p[1]]
                return file_name
                
            window = v2.MainWindow(l_stay[0])
            window.show()

            window1 = v2.MainWindow(p_in_no_p[0])
            window1.show()
            app.exec_()
