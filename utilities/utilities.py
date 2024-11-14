import numpy as np
import pandas as pd
from datetime import datetime, time
import os
from geopy.geocoders import Nominatim

# Map limits (top left, top right, bottom right, bottom left)
MAP_LIMITS_PAIR = ['-38.045359 145.278567', '-38.045359 145.296291',
                   '-38.057524 145.278567', '-38.057524 145.296291']

MAP_LIMITS = [['-38.045359', '145.278567'], ['-38.045359', '145.296291'],
              ['-38.057524', '145.278567'], ['-38.057524', '145.296291']]

MAP_LIMITS_FLOAT = [[-38.045359, 145.278567], [-38.045359, 145.296291],
                    [-38.057524, 145.296291], [-38.057524, 145.278567]]

ORMOND_LENGTH = 1.6  # KM
AMBERLY_LENGTH = 1.1  # KM

# Define public holidays (specific dates)
public_holidays = pd.to_datetime([
    "2024-01-01", "2024-01-26", "2024-03-11", "2024-03-29", "2024-03-30", "2024-03-31",
    "2024-04-01", "2024-04-25", "2024-06-10", "2024-09-27", "2024-11-05", "2024-12-25", "2024-12-26"
])

# Define school holidays (ranges of dates)
school_holidays = pd.to_datetime(np.concatenate([
    pd.date_range(start="2024-03-29", end="2024-04-14"),
    pd.date_range(start="2024-06-19", end="2024-07-14"),
    pd.date_range(start="2024-09-21", end="2024-10-06")
]))


def extract_coordinates_pair(snapped_path):
    coordinates = []
    # the coordinates are aplit with ",""
    for pair in snapped_path.split(','):
        try:
            coordinates.append(separate_coordinates(pair))
        except ValueError:
            continue
    return coordinates


def round_pair_lat_lon(lat, lon):
    return combine_coordinates(np.round(lon, 6), np.round(lat, 6))


def round_pair(pair):
    lon, lat = separate_coordinates(pair)
    return combine_coordinates(np.round(lon, 6), np.round(lat, 6))


def extract_coordinates(snapped_path):
    coordinates = []
    latitudes = []
    longitudes = []
    # the coordinates are aplit with ",""
    for pair in snapped_path.split(','):
        try:
            lon, lat = separate_coordinates(pair)
            coordinates.append(pair)
            latitudes.append(lat)
            longitudes.append(lon)
        except ValueError:
            pass
    return coordinates, latitudes, longitudes


def separate_coordinates(pair):
    p = pair.strip().split(' ')
    return (float(p[0]), float(p[1]))


def combine_coordinates(lon, lat):
    return str(lon) + ' ' + str(lat)


def clean_tag(stringpoint):
    start = stringpoint.find('(')
    point = stringpoint[start+1:]
    point = point.replace(')', '')
    point = point.replace('(', '')
    return point


def is_in_limits(lon, lat):
    flag = True
    if (lon < float(MAP_LIMITS[0][1]) or lon > float(MAP_LIMITS[1][1])
            or lat < float(MAP_LIMITS[2][0]) or lat > float(MAP_LIMITS[0][0])):
        flag = False
    return flag


def parse_speeds(speed_str):
    speeds_return = []
    ss = speed_str.split(',')
    # print(ss)
    for s in ss:
        speeds_return.append(float(s))
    return speeds_return


def parse_timestamps(timestamp_str):
    timestamp_str = timestamp_str.strip('[]')
    timestamp_list = [ts.strip()
                      for ts in timestamp_str.split(',') if ts.strip()]
    path = []
    for ts in timestamp_list:
        try:
            path.append(datetime.strptime(ts[:19], '%Y-%m-%d %H:%M:%S'))
        except ValueError:
            print(f"Failed to parse timestamp: {ts}")
    return path


def pad_or_truncate_trajectory(trajectory, length=10):
    if len(trajectory) > length:
        return trajectory[:length]
    else:
        return trajectory + [(0, 0)] * (length - len(trajectory))


def coordinates_to_fixed_length_vector(coords, length=10):
    padded_coords = pad_or_truncate_trajectory(coords, length)
    return [item for sublist in padded_coords for item in sublist]


def categorize_time(timestamp):
    # time periods
    dropoff_start = time(8, 0)
    dropoff_end = time(9, 30)
    pickup_start = time(14, 0)
    pickup_end = time(16, 0)
    bumper_morning_end = time(8, 0)
    bumper_morning_late_start = time(9, 30)
    bumper_afternoon_end = time(14, 0)
    bumper_afternoon_late_start = time(16, 0)
    # compariosn for the bumper and all the other times
    if timestamp.weekday() >= 5:
        return 'weekend'
    elif timestamp.date() in public_holidays:
        return 'public_holidays'
    elif timestamp.date() in school_holidays:
        return 'school_holidays'
    elif pickup_start <= timestamp.time() <= pickup_end:
        return 'pickup'
    elif dropoff_start <= timestamp.time() <= dropoff_end:
        return 'dropoff'
    elif (timestamp.time() < bumper_morning_end or
          bumper_morning_late_start < timestamp.time() or
          timestamp.time() < bumper_afternoon_end or
          bumper_afternoon_late_start < timestamp.time()):
        return 'bumper'
    else:
        return 'other'


def read_csv_files(folder_path):
    csv_files_name = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    csv_files = [pd.read_csv(folder_path+'/'+f) for f in csv_files_name]
    # print(csv_files)
    try:
        data = pd.concat(csv_files, ignore_index=True)
    except Exception:
        print("No files in the folder to analyse.")
        data = None
    return data


def filter_data(data):
    data_pick = []
    data_drop = []
    data_bumper = []
    data_weekend = []
    data_public_holiday = []
    data_school_holiday = []
    index = [set(), set(), set(), set(), set(), set()]
    try:
        parsed_timestamps = data['TimestampPath'].apply(parse_timestamps)
        parsed_coordinates = data['SnappedPath'].apply(
            extract_coordinates_pair)
        parsed_speeds = data['SpeedPath'].apply(parse_speeds)
    except Exception:
        print("Files dont have the right format - Ensure they are Compass IoT files")
        return None
    # print(parsed_timestamps)
    # print(parsed_coordinates)
    for i in parsed_coordinates.index:
        pick = []
        drop = []
        bumper = []
        weekend = []
        public_holiday = []
        school_holiday = []

        length = len(parsed_coordinates[i])
        for j in range(length):
            # print(parsed_coordinates[i][j])
            if (is_in_limits(parsed_coordinates[i][j][0], parsed_coordinates[i][j][1])):
                # print(parsed_timestamps[i])
                category = categorize_time(parsed_timestamps[i][j])
                # print(parsed_timestamps[i])
                # print(category)
                if (category == 'dropoff'):
                    drop.append(
                        [parsed_timestamps[i][j], parsed_coordinates[i][j], parsed_speeds[i][j]])
                    index[0].add(i)
                elif (category == 'pickup'):
                    pick.append(
                        [parsed_timestamps[i][j], parsed_coordinates[i][j], parsed_speeds[i][j]])
                    index[1].add(i)
                elif (category == 'bumper'):
                    bumper.append(
                        [parsed_timestamps[i][j], parsed_coordinates[i][j], parsed_speeds[i][j]])
                    index[2].add(i)
                elif (category == 'weekend'):
                    weekend.append(
                        [parsed_timestamps[i][j], parsed_coordinates[i][j], parsed_speeds[i][j]])
                    index[3].add(i)
                elif (category == 'public_holidays'):
                    public_holiday.append(
                        [parsed_timestamps[i][j], parsed_coordinates[i][j], parsed_speeds[i][j]])
                    index[4].add(i)
                elif (category == 'school_holidays'):
                    school_holiday.append(
                        [parsed_timestamps[i][j], parsed_coordinates[i][j], parsed_speeds[i][j]])
                    index[5].add(i)
                elif (category == 'other'):
                    continue
                    # print(parsed_timestamps[i][j])
        data_drop.append(drop)
        data_pick.append(pick)
        data_bumper.append(bumper)
        data_weekend.append(weekend)
        data_public_holiday.append(public_holiday)
        data_school_holiday.append(school_holiday)

    data_drop = clear_list(data_drop)
    data_pick = clear_list(data_pick)
    data_bumper = clear_list(data_bumper)
    data_weekend = clear_list(data_weekend)
    data_public_holiday = clear_list(data_public_holiday)
    data_school_holiday = clear_list(data_school_holiday)

    return [data_drop, data_pick, data_bumper, data_weekend, data_public_holiday, data_school_holiday, index]


def clear_list(list):
    return [x for x in list if x != []]


def get_road_name(lat, lon):
    attempts = 0
    road_name = ""
    geolocator = Nominatim(user_agent="abcd")
    while (attempts < 10):
        try:
            location = geolocator.reverse((lon, lat), exactly_one=True)
            if location and 'road' in location.raw['address']:
                road_name = location.raw['address']['road']
            attempts = 10
        except Exception:
            # print("error")
            attempts = attempts + 1
    return road_name


# Function to calculate unique weekdays, weekends, public holidays, and school holidays - ensure that each day is counted only once, regardless of how many times it appears in the data
def calculate_unique_days(data, index):
    # Drop rows with invalid dates
    data = data.iloc[index]
    valid_data = data.dropna(subset=['StartDate', 'EndDate'])

    # Sets to hold unique days
    unique_weekdays = set()
    unique_weekends = set()
    unique_public_holidays = set()
    unique_school_holidays = set()

    # Classify days
    for index, row in valid_data.iterrows():
        trip_days = pd.date_range(row['StartDate'], row['EndDate'])

        # Classify each day in the range
        for day in trip_days:
            # checks for public holidays and school holidays before classifying a day as a weekday or weekend. If a day is classified as a public holiday or school holiday, it is not double-counted as a weekday or weekend
            if day in public_holidays:
                unique_public_holidays.add(day)
            elif day in school_holidays:
                unique_school_holidays.add(day)
            elif day.weekday() < 5:  # Monday to Friday are weekdays (0-4)
                unique_weekdays.add(day)
            else:  # Saturday and Sunday are weekends (5-6)
                unique_weekends.add(day)

    # Calculate the total number of unique days
    total_unique_weekdays = 1 if len(
        unique_weekdays) == 0 else len(unique_weekdays)
    total_unique_weekends = 1 if len(
        unique_weekends) == 0 else len(unique_weekends)
    total_unique_public_holidays = 1 if len(
        unique_public_holidays) == 0 else len(unique_public_holidays)
    total_unique_school_holidays = 1 if len(
        unique_school_holidays) == 0 else len(unique_school_holidays)

    return total_unique_weekdays, total_unique_weekends, total_unique_public_holidays, total_unique_school_holidays


def calculate_averages(values, days):
    # print(values, days)
    return [np.round(values[0]/(days[0]*1.5), 3),
            np.round(values[1]/(days[0]*2), 3),
            np.round(values[2]/(days[0]*20.5), 3),
            np.round(values[3]/(days[1]*24), 3),
            np.round(values[4]/(days[2]*24), 3),
            np.round(values[5]/(days[3]*24), 3)]


def calculate_percentage(v1, v2):
    flag = (v1+v2)/2
    if (flag == 0):
        return 0
    return (v1-v2)/((v1+v2)/2)*100


def calculate_percentages(group):
    drop = []
    pick = []

    drop.append(calculate_percentage(group[0], group[2]))
    drop.append(calculate_percentage(group[0], group[3]))
    drop.append(calculate_percentage(group[0], group[4]))
    drop.append(calculate_percentage(group[0], group[5]))

    pick.append(calculate_percentage(group[1], group[2]))
    pick.append(calculate_percentage(group[1], group[3]))
    pick.append(calculate_percentage(group[1], group[4]))
    pick.append(calculate_percentage(group[1], group[5]))

    return (drop, pick)


def get_days(period, weekdays, weekend, p_holidays, s_holiday):
    days = (s_holiday, 24.0)
    if (period == "Drop off"):
        days = (weekdays, 1.5)
    elif (period == "Pick up"):
        days = (weekdays, 2.0)
    elif (period == "Weekdays - outside school hours"):
        days = (weekdays, 24)
    elif (period == "Weekends"):
        days = (weekend, 24)
    elif (period == "Public holidays"):
        days = (p_holidays, 24)
    elif (period == "Public holidays"):
        days = (s_holiday, 24)
    return days


def getDate(start, end):
    flag = True
    while (flag):
        try:
            date = pd.to_datetime(input(), dayfirst=True)
            if (date >= start and date <= end):
                flag = False
            else:
                print("Date is not in the range of " + start.strftime('%d-%m-%Y') +
                      " to " + end.strftime('%d-%m-%Y') + ", try again.")
        except BaseException:
            print("Input does not match date format, try again.")
    return date
