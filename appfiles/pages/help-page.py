import streamlit as st
import pandas as pd
import numpy as np
from menu import menu

menu()

st.title('Narre Warren South Traffic Project')
st.header('Help')

# Section: How the Program Works
st.subheader('1. How the Program Works')

# Subsection: Checking Files
st.write("""
The program analyzes CSV files provided by **Compass IoT** and **AeroRanger**. Before performing any analysis, ensure that the relevant files are uploaded to the correct directories:
- **Compass IoT files** should be added to the `data/files/CompassIoT` directory.
- **AeroRanger files** should be added to the `data/files/AeroRanger` directory.

Once the files are uploaded, the program will process them and allow you to generate reports.
""")

st.subheader("1.2 Running Analysis")
st.write("""
To analyze the files:
- For **Compass IoT analysis**, run the script:
    ```bash
    python CompassIoT.py
    ```
    The program will provide an option to create a report for **all data** or for a **custom period**.
    
- For **AeroRanger analysis**, run the script:
    ```bash
    python AeroRanger.py
    ```

After processing the data, the analysis will generate graphs and reports based on the following metrics:
- **Compass IoT**: Popular paths, speeding vehicles, destination in area, paths on main roads, car density.
- **AeroRanger**: Data filtered and analyzed similarly, providing visualizations for traffic patterns.
""")

st.subheader("1.3 Viewing Reports")
st.write("""
After running the analysis:
- The generated **PDF reports** will be saved in the `data/reports` directory.
- You can view the reports directly on the **Report** page of this web app or download them as PDF files.

These reports include visualizations such as bar graphs and maps, summarizing traffic patterns, vehicle density, and more.
""")

st.header("2. How to Navigate Through the Web Page")

st.subheader("2.1 Home Page")
st.write("""
The **Home** page provides an overview of the application, guiding you on how to use it for analyzing traffic data and generating reports.
""")

st.subheader("2.2 Files Page")
st.write("""
On the **Files** page, you can:
- View the existing **CSV files** from the `AeroRanger` and `CompassIoT` folders.
- Upload new CSV files to these folders using the interface.
- Select files for analysis by checking the boxes next to them.
""")

st.subheader("2.3 Analysis Page")
st.write("""
The **Analysis** page allows you to:
- Choose which vendor's data to analyze: **Compass IoT** or **AeroRanger**.
- Specify a **date range** for the analysis or use all data.
- View the results in the form of graphs, metrics, and visualizations that represent traffic patterns, speeding vehicles, and more.
""")

st.subheader("2.4 Report Page")
st.write("""
The **Report** page provides:
- A list of all generated **PDF reports**, with options to view or download each report.
- Visualizations such as bar graphs, heatmaps, or maps summarizing traffic data.
""")

st.subheader("2.5 Help Page")
st.write("""
The **Help** page (this page) explains how to navigate the web app and use the program effectively, guiding you through checking files, running analyses, and viewing or downloading reports.
""")

st.header("3. Metrics Descriptions")
st.subheader("3.1 Compass IoT")
st.write("""The metrics calculated for the data provided by Compass IoT will be divided into 6 different periods:

- Drop Off: Monday to Friday from 8:00 am to 9:30 am
- Pick Up: Monday to Friday from 2:00 pm to 4:00 pm
- Weekdays: Monday to Friday from 0:00 am to 8:00 am, 9:30 am to 2:00 pm and 4:00 pm to 12:00 am
- Weekends: Saturday and Sunday
- Public Holidays: Australian public holidays all-day
- School Holidays: Australian School Holidays all-day

The area under study used for the analysis surrounds the school, as seen in the image below.
[Study Area Map](/map_area.png)

For this analysis, the roads that limit the school are what the document refers to as the main roads. These roads are:

- Ormond Road
- Amberly Park Drive

For each period, the metrics are reported as the total number of occurrences in the file and the hourly average of these occurrences.
The hourly average is the result of dividing the total number of occurrences by the number of hours included in each period.
Example: if the file contains 2 weeks' worth of data, then for the pick-up period, the total hours for the period are 10 days \* 2 hours = 20 hours.
If the total number of occurrences in those two weeks for the pick-up period of a specific metric is 15 occurrences, then the hourly average for the period will be 15 occurrences / 20 hours = 0.75 occurrences per hour.

The calculation of the metrics is as follows:

- Popular paths: Vehicle Coordinates are bundled into "clusters"/"trajectories" by comparing them over a certain length. If one or more vehicles fall under that cluster, the path count increases, thus increasing the path's popularity.
- Speeding vehicles: Speeding vehicles are identified if they speed from more than 80% of their registered path. This is done by comparing each individual speed entry in the speed path with the speed limits at the time the speed is recorded.
- Destination in the area: The endpoint of each path determines whether the path destination is inside the school area under study.
- Path in main roads: By using an API, the coordinates of each trajectory were checked to see if paths were on any of the main roads. If the path stays for more than 80% of its trajectory within the main roads, it will be counted as a path in the main road; any other paths are counted as avoiding the main roads.
- Car density on main roads: The calculation for this metric counts all the cars that go through the main roads and then divides this by the length of the road. The length of the roads was estimated by using information from Google maps.""")