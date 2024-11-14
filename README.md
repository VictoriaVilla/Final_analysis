# Data Analytics for traffic hazards identification

The following script will analyze CSV files provided by Compass IoT and provide a set of maps, graphs and a text report that will facilitate the corroboration of the community concerns in relation to the Rat Racing and High traffic in the School area.

## Usage

Ensure the installation of the latest [Python](https://www.python.org/downloads/) library and [pip](https://pip.pypa.io/en/stable/).

Directory of application should look as below.

```bash
│
├───analysis
├───data
│   ├───files
│   │   ├───CompassIoT
│   │   └───AeroRanger
│   ├───reports
│   └───temp
├───reporting
├───utilities
└───visualization
```

To run the application:

### For Compass IoT analysis:

1. add the Compass IoT files in the data/files/CompassIoT directory.
2. Then in the root directory for the project run

```bash
python compassiot.py
```

3. After the compilation of the files a terminal interface will be allow the user to select the creation of a report wil all the data from the files or a report fo a custom period.
   "Want report created with all data (all) or a custom period (custom)?"
   If option selected is custom it will require to two dates, the start date and end date for the report.
   "Enter start date for custom period (dd/mm/yyyy):"
   "Enter end date for custom period (dd/mm/yyyy):"
   After finalizing the report creation there will be an option to create another report.
4. PDF report is located on the data/reports directory

### For AeroRanger analysis:

1. add the AeroRanger files in the data/files/CompassIoT directory.
2. Then in the root directory for the project run

```bash
python aeroranger.py
```

### For Web App:

1. In the root directory for the project run

```bash
python app.py
```

## Notes

The following notes describe the methods used to calculate the different metrics reported:

### Compass IoT

The metrics calculated for the data provided by Compass IoT will be divided into 6 different periods:

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
- Car density on main roads: The calculation for this metric counts all the cars that go through the main roads and then divides this by the length of the road. The length of the roads was estimated by using information from Google maps.

### AeroRanger

The metrics calculated for the data provided by AeroRanger as are follows:

- Long stay parking:
- Parking in no Parking areas:
