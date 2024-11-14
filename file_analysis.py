from analysis import analysis as a
from visualization import visualization as v
from reporting import textfilecreator as tfc
import sys
from utilities import utilities as ut
from PyQt5.QtWidgets import QApplication
import datetime
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd
import streamlit as st


def run_analysis(selected_files, interface, start_date, end_date, app):
    # Read files in the data/files (Compass IoT) folder
    path = 'data/files/CompassIoT/'
    print("Compass IoT analysis started\nCompiling files...")
    if interface == "app":
        st.write("Compass IoT analysis started")
        st.write("Compiling files...")
    data = ut.read_csv_files(path)
    if (data is None):
        print("Compiling files failed - analysis cancelled")
        if interface == "app":
            st.write("Compiling files failed - analysis cancelled")
        fd = None
        # failed
    else:
        report_flag = True
        while (report_flag):
            print("Files compiled.")
            if interface == "app":
                st.write("Files compiled.")
            if (interface == "terminal"):
                # filter data into periods and inside of school
                start_data = pd.to_datetime(data['StartDate']).min()
                end_data = pd.to_datetime(data['EndDate']).max()
                options_flag = True
                option = ""
                df = data
                while (options_flag):
                    print(
                        "Want report created with all data (all) or a custom period (custom)?")
                    option = input().casefold()
                    if (option == "all"):
                        options_flag = False
                        s_date = start_data
                        e_date = end_data
                    elif (option == "custom"):
                        options_flag = False
                        print("Data available from " + start_data.strftime('%d-%m-%Y') +
                              " to " + end_data.strftime('%d-%m-%Y'))
                        print("Enter start date for custom period (dd/mm/yyyy):")
                        # s_date = pd.to_datetime(
                        # "01/02/2024", dayfirst=True)
                        s_date = ut.getDate(start_data, end_data)
                        print("Enter end date for custom period (dd/mm/yyyy):")
                        # e_date = pd.to_datetime(
                        # "02/02/2024", dayfirst=True) + datetime.timedelta(days=1)
                        # e_date = e_date - datetime.timedelta(minutes=1)
                        e_date = ut.getDate(start_data, end_data) + \
                            datetime.timedelta(days=1)
                        # e_date = e_date - datetime.timedelta(minutes=1)
                    else:
                        print("\"" + option +
                              "\" is not an option, please try again.")
            elif (interface == "app"):
                data = pd.concat([pd.read_csv(path+file)
                                 for file in selected_files], ignore_index=True)
                # print(data)
                s_date = pd.to_datetime(start_date)
                e_date = pd.to_datetime(end_date)
                e_date = e_date - datetime.timedelta(minutes=1)
            df = data[pd.to_datetime(
                data["StartDate"]) >= s_date]
            df = df[pd.to_datetime(df["EndDate"]) <= e_date]
            print("Filtering data files...")
            if interface == "app":
                st.write("Filtering data files...")
            fd = ut.filter_data(df)

            if fd is None:
                print("Filtering failed - analysis cancelled")
                if interface == "app":
                    st.write("Filtering failed - analysis cancelled")
            else:
                filtered_data = fd[:6]
                index = list(fd[-1])
                print("Data filtered.")
                if interface == "app":
                    st.write("Data filtered.")

                # variables
                vehicles_in_area = []
                destination_in_area = []
                popular_paths = []
                paths_in_main_rd = []
                paths_avoid_main_rd = []
                paths_errors = []
                paths_skipped = []
                speeding_vehicles = []
                stopped_vehicles = []
                car_density_ormond = []
                car_density_amberly = []
                periods = ["Drop off", "Pick up", "Weekdays - outside school hours",
                           "Weekends", "Public holidays", "School holidays"]

                index_list = list(index[0]) + list(index[1]) + list(index[2]) + \
                    list(index[3]) + list(index[4]) + list(index[5])
                index_list.sort()
                # calculate Hourly averages fro analysis
                print("Calculating days...")
                if interface == "app":
                    st.write("Calculating days...")
                weekdays, weekend, p_holidays, s_holiday = ut.calculate_unique_days(
                    data, index_list)
                days = [weekdays, weekend, p_holidays, s_holiday]
                print("Days calculated.")
                print("Starting the analysis...")
                if interface == "app":
                    st.write("Days calculated.")
                    st.write("Starting the analysis...")
                for period_data, period, ind in zip(filtered_data, periods, index):
                    print("Analyzing " + str(period) + " data...")
                    if interface == "app":
                        st.write("Analyzing " + str(period) + " data...")
                    # speeding
                    speeding, not_speeding, coord = a.speeding_vehicles(
                        period_data, period)
                    speeding_vehicles.append(speeding)
                    # traffic
                    vehicles_in_area.append(len(period_data))
                    destination_in_area.append(
                        a.destination_in_area(data, ind))
                    popular_paths.append(a.popular_paths(period_data))
                    orm, amb = a.main_roads_density(period_data)
                    car_density_ormond.append(orm)
                    car_density_amberly.append(amb)
                    stopped_vehicles.append(
                        a.stopped_vehicles(period_data))

                    # rat racing
                    path_in_main, path_avoid, path_error, path_too_short = a.path_in_main_roads(
                        period_data)
                    paths_in_main_rd.append(path_in_main)
                    paths_avoid_main_rd.append(path_avoid)
                    paths_errors.append(path_error)
                    paths_skipped.append(path_too_short)
                    print("Analysis for " + str(period) + " data complete.")
                    if interface == "app":
                        st.write("Analysis for " +
                                 str(period) + " data complete.")
                print("Analysis finished.")
                print("Calculating Hourly averages...")
                if interface == "app":
                    st.write("Analysis finished.")
                    st.write("Calculating Hourly averages...")
                hourly_average_speeding = [] if len(
                    speeding_vehicles) == 0 else ut.calculate_averages(speeding_vehicles, days)
                hourly_average_veh_in_area = [] if len(
                    vehicles_in_area) == 0 else ut.calculate_averages(vehicles_in_area, days)
                hourly_average_destination_in_area = [] if len(
                    destination_in_area) == 0 else ut.calculate_averages(
                    destination_in_area, days)
                hourly_average_paths_in_main_rd = [] if len(
                    paths_in_main_rd) == 0 else ut.calculate_averages(paths_in_main_rd, days)
                hourly_average_paths_avoid_main_rd = [] if len(
                    paths_avoid_main_rd) == 0 else ut.calculate_averages(
                    paths_avoid_main_rd, days)
                hourly_average_car_density_ormond = []if len(
                    car_density_ormond) == 0 else ut.calculate_averages(
                    car_density_ormond, days)
                hourly_average_car_density_amberly = []if len(
                    car_density_amberly) == 0 else ut.calculate_averages(
                    car_density_amberly, days)
                print("Averages calculated.")
                if interface == "app":
                    st.write("Averages calculated.")
                # Calculate difference percentages
                drop_veh_in_area, pick_veh_in_area = ut.calculate_percentages(
                    hourly_average_veh_in_area)
                drop_destination_in_area, pick_destination_in_area = ut.calculate_percentages(
                    hourly_average_destination_in_area)
                drop_paths_in_main_rd, pick_paths_in_main_rd = ut.calculate_percentages(
                    hourly_average_paths_in_main_rd)
                drop_paths_avoid_main_rd, pick_paths_avoid_main_rd = ut.calculate_percentages(
                    hourly_average_paths_avoid_main_rd)

                # creating File for report
                ct = datetime.datetime.now()
                # file = tfc.getFile('report' + ct.strftime("%m-%d-%Y-%H-%M") + '.txt')
                # pdf_buffer = BytesIO()
                # file = SimpleDocTemplate(pdf_buffer)
                sample_style_sheet = getSampleStyleSheet()
                elements = []
                file_name = 'data/reports/CompassIoT-report-' + \
                    ct.strftime("%d-%m-%Y-%H-%M") + '.pdf'
                file = SimpleDocTemplate(file_name, pagesize=letter)
                # reporting
                elements.append(Paragraph(
                    "Findings of the analysis of Compass IOT data.", sample_style_sheet['Heading1']))
                elements.append(Paragraph(
                    s_date.strftime("%d-%m-%Y")
                    + " - " + e_date.strftime("%d-%m-%Y"), sample_style_sheet['Heading1']))
                elements.append(Paragraph("Individual period analysis",
                                          sample_style_sheet['Heading1']))

                for i in range(len(periods)):
                    days = ut.get_days(periods[i], weekdays,
                                       weekend, p_holidays, s_holiday)
                    values = [[Paragraph(periods[i] + " period", sample_style_sheet['Heading2'])],
                              [Paragraph("Days analysed:", sample_style_sheet['BodyText']), str(
                                  days[0]), ""],
                              [Paragraph("Hours analysed:", sample_style_sheet['BodyText']), str(
                                  days[0]*days[1]), ""],
                              [Paragraph("Traffic Analysis",
                                         sample_style_sheet['BodyText']), "", ""],
                              [Paragraph("Vehicles in the area:",
                                         sample_style_sheet['BodyText']), "", ""],
                              ["", "Total vehicles in data:",
                                   str(vehicles_in_area[i])],
                              ["", "Hourly average:", str(
                                  hourly_average_veh_in_area[i])],
                              [Paragraph("Destination in the area:",
                                         sample_style_sheet['BodyText']), "", ""],
                              ["", "Total vehicles in data:", str(
                                  destination_in_area[i])],
                              ["", "Hourly average:", str(
                                  hourly_average_destination_in_area[i])],
                              [Paragraph("Car Density in Ormond Road (Main Road):",
                                         sample_style_sheet['BodyText']), "", ""],
                              ["", "Total vehicles per KM:", str(
                                  car_density_ormond[i])],
                              ["", "Hourly average:", str(
                                  hourly_average_car_density_ormond[i])],
                              [Paragraph("Car Density in Amberly Road (Main Road):",
                                         sample_style_sheet['BodyText']), "", ""],
                              ["", "Total vehicles per KM:", str(
                                  car_density_amberly[i])],
                              ["", "Hourly average:", str(
                                  hourly_average_car_density_amberly[i])],
                              [Paragraph("Speeding Analysis",
                                         sample_style_sheet['BodyText']), "", ""],
                              [Paragraph("Vehicles that speed more than 80% of their trajectory:",
                                         sample_style_sheet['BodyText']), "", ""],
                              ["", "Total Vehicles in data:",
                                   str(speeding_vehicles[i])],
                              ["", "Hourly average:", str(
                                  hourly_average_speeding[i])],
                              [Paragraph("Rat Racing Analysis",
                                         sample_style_sheet['BodyText']), ""],
                              [Paragraph("Paths going through main roads:",
                                         sample_style_sheet['BodyText']), ""],
                              ["", "Total paths in data:",
                                   str(paths_in_main_rd[i])],
                              ["", "Hourly average:", str(
                                  hourly_average_paths_in_main_rd[i])],
                              [Paragraph("Paths avoiding main roads:",
                                         sample_style_sheet['BodyText']), ""],
                              ["", "Total paths in data:", str(
                                  paths_avoid_main_rd[i])],
                              ["", "Hourly average:", str(
                                  hourly_average_paths_avoid_main_rd[i])]]

                    elements.append(tfc.toTable(values))

                    if (len(filtered_data[i]) != 0):
                        elements.append(Paragraph("\nFor Car Density and rat racing analysis paths shorter than 10 coordinates were skipped\n\t"
                                                  + str(paths_skipped[i])
                                                  + " paths were skipped which represents the "
                                                  + str(np.round((paths_skipped[i]*100)/len(filtered_data[i]), 3))
                                                  + "% of all the paths", sample_style_sheet['BodyText']))
                    if (len(filtered_data[i]) != 0):
                        elements.append(Paragraph("Some paths could not be identified\n\t" + str(paths_errors[i])
                                                  + " paths were not identifiable which represents the "
                                                  + str(np.round((paths_errors[i]*100)/len(filtered_data[i]), 3))
                                                  + "% of all the paths", sample_style_sheet['BodyText']))
                    elements.append(PageBreak())

                    elements.append(Paragraph(
                        "\n\nComparison of hourly averages\n\n", sample_style_sheet['Heading1']))
                    elements.append(Paragraph("Traffic Analysis\n",
                                    sample_style_sheet['Heading2']))

                    heading = [Paragraph("Analysis", sample_style_sheet['BodyText']),
                               Paragraph(
                        periods[0], sample_style_sheet['BodyText']),
                        Paragraph(
                        periods[1], sample_style_sheet['BodyText']),
                        Paragraph(
                        periods[2], sample_style_sheet['BodyText']),
                        Paragraph(
                        periods[3], sample_style_sheet['BodyText']),
                        Paragraph(
                        periods[4], sample_style_sheet['BodyText']),
                        Paragraph(periods[5], sample_style_sheet['BodyText'])]

                    values = [heading,
                              [Paragraph("Paths going through main roads", sample_style_sheet['BodyText']),
                               hourly_average_paths_in_main_rd[0],
                               hourly_average_paths_in_main_rd[1], hourly_average_paths_in_main_rd[2],
                               hourly_average_paths_in_main_rd[3], hourly_average_paths_in_main_rd[4],
                               hourly_average_paths_in_main_rd[5]],
                              [Paragraph("Destination in the area", sample_style_sheet['BodyText']),
                                  hourly_average_destination_in_area[0],
                                  hourly_average_destination_in_area[1], hourly_average_destination_in_area[2],
                                  hourly_average_destination_in_area[3], hourly_average_destination_in_area[4],
                                  hourly_average_destination_in_area[5]],
                              [Paragraph("Car Density in Ormond Road (Main Road)", sample_style_sheet['BodyText']),
                                  hourly_average_car_density_ormond[0],
                                  hourly_average_car_density_ormond[1], hourly_average_car_density_ormond[2],
                                  hourly_average_car_density_ormond[3], hourly_average_car_density_ormond[4],
                                  hourly_average_car_density_ormond[5]],
                              [Paragraph("Car Density in Amberly Road (Main Road)", sample_style_sheet['BodyText']),
                                  hourly_average_car_density_amberly[0],
                                  hourly_average_car_density_amberly[1], hourly_average_car_density_amberly[2],
                                  hourly_average_car_density_amberly[3], hourly_average_car_density_amberly[4],
                                  hourly_average_car_density_amberly[5]]]

                    elements.append(tfc.toComparasonTable(values))

                    elements.append(Paragraph("Speeding Analysis\n",
                                    sample_style_sheet['Heading2']))

                    values = [heading,
                              [Paragraph("Vehicles that speed more than 80% of their trajectory", sample_style_sheet['BodyText']),
                               hourly_average_speeding[0],
                               hourly_average_speeding[1], hourly_average_speeding[2],
                               hourly_average_speeding[3], hourly_average_speeding[4],
                               hourly_average_speeding[5]]]

                    elements.append(tfc.toComparasonTable(values))

                    elements.append(Paragraph("Rat Racing Analysis\n",
                                    sample_style_sheet['Heading2']))

                    values = [heading,
                              [Paragraph("Paths on the main roads", sample_style_sheet['BodyText']),
                               hourly_average_veh_in_area[0],
                               hourly_average_veh_in_area[1], hourly_average_veh_in_area[2],
                               hourly_average_veh_in_area[3], hourly_average_veh_in_area[4],
                               hourly_average_veh_in_area[5]],
                              [Paragraph("Paths avoiding main roads", sample_style_sheet['BodyText']),
                                  hourly_average_paths_avoid_main_rd[0],
                                  hourly_average_paths_avoid_main_rd[1], hourly_average_paths_avoid_main_rd[2],
                                  hourly_average_paths_avoid_main_rd[3], hourly_average_paths_avoid_main_rd[4],
                                  hourly_average_paths_avoid_main_rd[5]]]

                    elements.append(tfc.toComparasonTable(values))

                file.build(elements)

                # test data
                '''hourly_average_speeding = [1, 2, 3, 4, 5, 6]
                    hourly_average_veh_in_area = [1, 2, 3, 4, 5, 6]
                    hourly_average_destination_in_area = [1, 2, 3, 4, 5, 6]
                    hourly_average_paths_in_main_rd = [1, 2, 3, 4, 5, 6]
                    hourly_average_paths_avoid_main_rd = [1, 2, 3, 4, 5, 6]
                    hourly_average_car_density_ormond = [1, 2, 3, 4, 5, 6]
                    hourly_average_car_density_amberly = [1, 2, 3, 4, 5, 6]
                    periods = ["Drop off", "Pick up", "Weekdays - outside school hours",
                            "Weekends", "Public holidays", "School holidays"]
                    headers = ["Analysis", periods[0], periods[1],
                            periods[2], periods[3], periods[4], periods[5]]
                    values = [["Analysis", periods[0], periods[1],
                            periods[2], periods[3], periods[4], periods[5]],
                            ["Vehicles in the area", hourly_average_veh_in_area[0],
                            hourly_average_veh_in_area[1], hourly_average_veh_in_area[2],
                            hourly_average_veh_in_area[3], hourly_average_veh_in_area[4],
                            hourly_average_veh_in_area[5]],
                            ["Paths avoiding main roads", hourly_average_paths_avoid_main_rd[0],
                            hourly_average_paths_avoid_main_rd[1], hourly_average_paths_avoid_main_rd[2],
                            hourly_average_paths_avoid_main_rd[3], hourly_average_paths_avoid_main_rd[4],
                            hourly_average_paths_avoid_main_rd[5]]]'''

                if interface == "app":
                    st.write("Creating Maps and Plots.")
                    st.write(
                        "White windows might pop up, and close by themselves.")
                paths_plotted = v.plot_paths(
                    popular_paths, periods, "Popular Paths", file_name)
                veh_area = v.create_bar_graphs(
                    hourly_average_veh_in_area,  "Vehicles in the Area", file_name)
                destination_in_area = v.create_bar_graphs(
                    hourly_average_destination_in_area, "Destination in the Area", file_name)
                speeding = v.create_bar_graphs(
                    hourly_average_speeding, "Speeding in the Area", file_name)
                paths_in_main_rd = v.create_bar_graphs(
                    hourly_average_paths_in_main_rd, "Paths in Main roads (Ormond Road or Amberly Park Drive)", file_name)
                avoid_main_rd = v.create_bar_graphs(
                    hourly_average_paths_avoid_main_rd,
                    "Paths avoiding Main roads (Ormond Road or Amberly Drive)", file_name)
                density_ormond = v.create_bar_graphs(
                    hourly_average_car_density_ormond,
                    "Vehicle density Ormond Road", file_name)
                density_amberly = v.create_bar_graphs(
                    hourly_average_car_density_amberly,
                    "Vehicle density Amberly Park Drive", file_name)
                if interface == "app":
                    st.write("Maps and Plots created.")
                    st.session_state.maps_c = paths_plotted[1]
                    st.session_state.graphs_c = [veh_area[0], destination_in_area[0], speeding[0],
                                                 paths_in_main_rd[0], avoid_main_rd[0], density_ormond[0], density_amberly[0]]
                # plotting maps and bar graphs
                if (interface == "app"):
                    return file_name
                
                w_popular = v.MapWindow(
                    paths_plotted[0], periods, "Popular Paths")
                w_popular.show()

                w_veh_area = v.BarWindow(
                    veh_area[0], "Vehicles in the Area")
                w_veh_area.show()

                w_destination_in_area = v.BarWindow(
                    destination_in_area[0], "Destination in the Area")
                w_destination_in_area.show()

                w_speeding = v.BarWindow(
                    speeding[0], "Speeding in the Area")
                w_speeding.show()

                w_paths_in_main_rd = v.BarWindow(
                    paths_in_main_rd[0], "Paths in Main roads (Ormond Road or Amberly Park Drive)")
                w_paths_in_main_rd.show()

                w_avoid_main_rd = v.BarWindow(
                    avoid_main_rd[0], "Paths avoiding Main roads (Ormond Road or Amberly Drive)")
                w_avoid_main_rd.show()

                w_density_ormond = v.BarWindow(
                    density_ormond[0], "Vehicle density Ormond Road")
                w_density_ormond.show()

                w_density_amberly = v.BarWindow(density_amberly[0],
                                                "Vehicle density Amberly Park Drive")
                w_density_amberly.show()

                print("Want to create another report? (y/n)")
                new_report_flag = True
                while (new_report_flag):
                    report = input().casefold()
                    if (report == "y"):
                        new_report_flag = False
                    elif (report == "n"):
                        report_flag = False
                        new_report_flag = False
                    else:
                        print("\"" + report +"\" is not a valid option, try again.")
                print("To continue close all maps and charts windows")

                app.exec_()
