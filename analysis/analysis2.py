import pandas as pd
from datetime import datetime


def long_stay(df):
    df['Time'] = pd.to_datetime(df['Time'], format="%d/%m/%Y %H:%M")

    # rounding lat and lon to a lower decimal place as the lat and lons are never exactly the same, hence making location comparisons without rounding impossible
    # change according to decimal places required, this currently rounds to 5 decimal places
    df['Latitude'] = df['Latitude'].round(5)
    df['Longitude'] = df['Longitude'].round(5)

    df = df.sort_values(by=['Plate', 'Time'])

    long_stays = []
    # define how many hours incurs a long stay, used 1 for debugging purposes
    # defined as 24 hours
    threshold_hours = 24

    for plate, group in df.groupby('Plate'):  # group every plate together
        group = group.reset_index(drop=True)
        for i in range(1, len(group)):
            # compare rounded Latitude and Longitude values
            if (group.loc[i, 'Latitude'] == group.loc[i-1, 'Latitude'] and
                    group.loc[i, 'Longitude'] == group.loc[i-1, 'Longitude']):
                # when location and plate is same, check how long the time difference is between the two rows
                time_diff = (group.loc[i, 'Time'] -
                             group.loc[i-1, 'Time']).total_seconds() / 3600
                if time_diff >= threshold_hours:  # long stay parking identified whenever time difference is higher than previously defined time limit
                    long_stays.append({  # add to the array
                        'plate': plate,
                        'start_time': group.loc[i-1, 'Time'],
                        'end_time': group.loc[i, 'Time'],
                        'duration_hours': time_diff,
                        'Latitude': group.loc[i, 'Latitude'],
                        'Longitude': group.loc[i, 'Longitude']
                    })

    # convert results to DataFrame and display
    return pd.DataFrame(long_stays)


def parking_in_no_parking(df):

    df['Time'] = pd.to_datetime(df['Time'], format='%d/%m/%Y %H:%M')

    # No parking time range
    morning_start = datetime.strptime("08:30", "%H:%M").time()
    morning_end = datetime.strptime("09:15", "%H:%M").time()
    afternoon_start = datetime.strptime("15:00", "%H:%M").time()
    afternoon_end = datetime.strptime("15:30", "%H:%M").time()

    # Filter 1: 'No Parking Amberly Park drive' zone and within time ranges
    zone_filter1 = df['Zones'] == 'No Parking Amberly Park drive'
    time_filter = df['Time'].dt.time.between(
        morning_start, morning_end) | df['Time'].dt.time.between(afternoon_start, afternoon_end)
    amberly_park_filtered = df[zone_filter1 & time_filter]

    # Filter 2: 'School Court' zone and Camera ID is 1
    zone_filter2 = df['Zones'] == 'School Court'
    camera_filter = df['Camera ID'] == 1
    school_court_filtered = df[zone_filter2 & camera_filter]

    return pd.concat([amberly_park_filtered, school_court_filtered])
