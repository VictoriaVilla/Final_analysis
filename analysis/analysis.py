import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from collections import Counter
from utilities import utilities as ut


def popular_paths(data):
    return_paths = []
    if len(data) != 0:
        all_coords = []
        for d in data:
            c = []
            for i in range(len(d)):
                c.append(d[i][1])
            all_coords.append(c)

        # getting unique rows because itll override rows
        unique_coords = [list(t) for t in set(tuple(path)
                                              for path in all_coords)]

        fixed_length_vectors = [ut.coordinates_to_fixed_length_vector(
            path) for path in unique_coords]

        fixed_length_vectors_array = np.asarray(
            fixed_length_vectors, dtype="object")

        scaler = StandardScaler()
        scaled_vectors = scaler.fit_transform(fixed_length_vectors_array)

        db = DBSCAN(eps=0.001, min_samples=2,
                    metric='euclidean').fit(scaled_vectors)
        labels = db.labels_

        # creating cluster for paths
        clustered_paths = {}
        for i, label in enumerate(labels):
            if label != -1:
                clustered_paths.setdefault(label, []).append(unique_coords[i])

        # Counting cluster repetitions
        cluster_sizes = Counter(labels[labels != -1])
        clusters = cluster_sizes.most_common(10)

        # Creating tuple array with path and number of repetitions

        for idx, (label, number) in enumerate(clusters):
            for path in clustered_paths[label]:
                return_paths.append((path, number))
    return return_paths


def stopped_vehicles(data):
    lat = []
    lon = []

    # getting list of coordinates and speeds
    for i in range(len(data)):
        for j in range(len(data[i])):

            # finding indexes where speed is 0
            index = np.where(data[i][j][2] == 0)

            # finding coordinates where speed is 0
            for ind in index[0]:
                lat.append(data[i][ind][1][0])
                lon.append(data[i][ind][1][1])
    return (lat, lon)


def speeding_vehicles(data, period):
    coordinates = []
    speed_limit = 60
    count = []

    if (period == "dropoff" or period == "pickup"):
        speed_limit = 40

    # getting list of coordinates and speeds
    for i in range(len(data)):
        count_speeding = 0
        count_not_speeding = 0
        coo = []
        for j in range(len(data[i])):
            if (data[i][j][2] >= speed_limit):
                # finding indexes where speed is 0
                count_speeding += 1
                coo.append(data[i][j][1])
            else:
                count_not_speeding += 1
        count.append((count_speeding, count_not_speeding))
        coordinates.append(coo)
    coordinates = ut.clear_list(coordinates)
    speeding = 0
    not_speeding = 0
    for c in count:
        total = c[0]+c[1]
        if (total != 0):
            if (((c[0]*100)/total) > 80):
                speeding += 1
            else:
                not_speeding += 1
        # print(path_in_main, path_avoid, path_error)
    return (speeding, not_speeding, coordinates)


def destination_in_area(data, index):
    count = 0
    index_list = list(index)
    data = data.iloc[index_list]
    for d in data['EndPoint']:
        lat, lon = ut.separate_coordinates(ut.clean_tag(d))
        # print(lat, lon)
        if (ut.is_in_limits(lat, lon)):
            count = count+1
    return count


def path_in_main_roads(data):
    coordinates = []
    roads = []
    count = []  # count of ormond, error for each path
    path_in_main = 0
    path_avoid = 0
    path_error = 0
    path_too_short = 0
    if len(data) != 0:
        for d in data:
            roads_in_path = []
            count_main = 0
            count_other = 0
            count_err = 0
            size = len(d)
            divider = 40
            if (size < 10):
                path_too_short += 1
            else:
                if (size >= divider):
                    divider = 5
                for i in range(size):
                    if i % (divider) != 0:  # 30 takes - with 10 takes 6418.502 sec
                        continue  # Skip coordinates that are not every 10th to speed up process, can lower to make more accurate
                    coordinates.append(d[i][1])
                    road_name = ut.get_road_name(d[i][1][0], d[i][1][1])
                    roads_in_path.append(road_name)
                    # print(road_name)
                    if (road_name == "Ormond Road" or road_name == "Amberly Park Drive"):
                        count_main += 1
                    elif (road_name == ""):
                        count_err += 1
                    else:
                        count_other += 1
                    # print(count_main, count_other, count_err)
                roads.append(roads_in_path)
                count.append((count_main, count_other, count_err))
            # print(path_too_short)

        for c in count:
            total = c[0]+c[1]
            if (total != 0):
                if (((c[0]*100)/total) > 80):
                    path_in_main += 1
                else:
                    path_avoid += 1
            else:
                path_error += 1
        # print(path_in_main, path_avoid, path_error)
    return (path_in_main, path_avoid, path_error, path_too_short)


def main_roads_density(data):
    count = []  # count of ormond, error for each path
    path_in_Ormond = 0
    path_in_Amberly = 0
    path_too_short = 0
    if len(data) != 0:
        for d in data:
            count_ormond = 0
            count_amberly = 0
            size = len(d)
            divider = 40
            if (size < 10):
                path_too_short += 1
            else:
                if (size >= divider):
                    divider = 5
                for i in range(size):
                    if i % (divider) != 0:  # 30 takes - with 10 takes 6418.502 sec
                        continue  # Skip coordinates that are not every 10th to speed up process, can lower to make more accurate
                    # print(road_name)
                    road_name = ut.get_road_name(d[i][1][0], d[i][1][1])
                    if (road_name == "Ormond Road"):
                        count_ormond += 1
                    elif (road_name == "Amberly Park Drive"):
                        count_amberly += 1
                    # print(count_main, count_other, count_err)
                count.append(
                    (count_ormond, count_amberly))
            # print(path_too_short)

        for c in count:
            if (c[0] != 0):
                path_in_Ormond += 1
            if (c[1] != 0):
                path_in_Amberly += 1
    return (path_in_Ormond/ut.ORMOND_LENGTH, path_in_Amberly/ut.AMBERLY_LENGTH)
