import pandas as pd
from collections import defaultdict
# List of Australian states considered as "Australian States"
australian_states = ['NSW', 'VIC', 'QLD', 'SA', 'WA', 'TAS', 'NT', 'ACT']
car_make = ["TOYOTA", "T0YOTA", "TOY0TA", "T0Y0TA"]


def filter_plate_confidence(df):
    good_df = df[df['Plate Confidence'] >= 80]
    bad_df = df[df['Plate Confidence'] < 80]
    return good_df, bad_df


def filter_state(df):
    good_df = df[df['State'].isin(australian_states)]
    bad_df = df[~df['State'].isin(australian_states)]
    return good_df, bad_df


def filter_plate_duplicate(df):
    good_df = df[df.duplicated('Plate', keep=False)]
    bad_df = df.drop_duplicates('Plate', keep=False)
    return good_df, bad_df


def filter_bus(df):
    good_df = df[df['Vehicle Model'] != "generic_bus"]
    return good_df


def filter_car_make(df):
    good_df = df[~df['Plate'].isin(car_make)]
    bad_df = df[df['Plate'].isin(car_make)]
    return good_df, bad_df

# possible variations in plates


def correct_plate(plate, reference_plate):
    corrections = {
        '1': ['I', '7'],
        'I': ['1'],
        '8': ['B'],
        'B': ['8'],
        '0': ['O'],
        'O': ['0'],
        '5': ['S'],
        'S': ['5']
    }
    # getting the matching characters and increasing count
    corrected_plate = []
    match_count = 0
    for p_char, r_char in zip(plate, reference_plate):
        if p_char != r_char:
            if p_char in corrections and r_char in corrections[p_char]:
                corrected_plate.append(r_char)
                match_count += 1
            else:
                corrected_plate.append(p_char)
        else:
            corrected_plate.append(p_char)
            match_count += 1
    return ''.join(corrected_plate), match_count

# (@) using the vehicle details to know which plate is correct


def correct_similar_plates(plate_counts, plate_data):
    corrected_plate_counts = defaultdict(int)
    # just a small list to know which plate was wrong and how many times
    plate_corrections = defaultdict(list)
    corrections = []
    plates = list(plate_counts.keys())

    # (3) trying all possible combinatinations
    for i, plate in enumerate(plates):
        for j in range(i+1, len(plates)):
            similar_plate = plates[j]
            corrected_plate, match_count = correct_plate(plate, similar_plate)

            # 4 same characters as a base
            if match_count >= 4:
                vehicle1 = plate_data[plate_data['Plate'] == plate].iloc[0]
                vehicle2 = plate_data[plate_data['Plate']
                                      == similar_plate].iloc[0]
                # they all should be the same for it to even be considered
                if (vehicle1['Vehicle Model'] == vehicle2['Vehicle Model'] and
                    vehicle1['Vehicle Make'] == vehicle2['Vehicle Make'] and
                    vehicle1['Vehicle Body Type'] == vehicle2['Vehicle Body Type'] and
                        vehicle1['Vehicle Colour'] == vehicle2['Vehicle Colour']):
                    count_plate = plate_counts[plate]
                    count_similar_plate = plate_counts[similar_plate]
                    # using the confidence and all that to change wrong plate to correct plate
                    if count_plate > count_similar_plate:
                        correct_plate_number = plate
                        wrong_plate = similar_plate
                    elif count_similar_plate > count_plate:
                        correct_plate_number = similar_plate
                        wrong_plate = plate
                    else:
                        plate_confidence_plate = vehicle1['Plate Confidence']
                        plate_confidence_similar = vehicle2['Plate Confidence']
                        if plate_confidence_plate > plate_confidence_similar:
                            correct_plate_number = plate
                            wrong_plate = similar_plate
                        else:
                            correct_plate_number = similar_plate
                            wrong_plate = plate
                    plate_corrections[correct_plate_number].append(
                        (wrong_plate, plate_counts[wrong_plate]))
                    corrections.append([wrong_plate, correct_plate_number])
                    sorted_plate_corrections = dict(
                        sorted(plate_corrections.items()))

                    corrected_plate_counts[correct_plate_number] += count_plate + \
                        count_similar_plate
                    plate_counts.pop(plate, None)
                    plate_counts.pop(similar_plate, None)
    for plate, count in plate_counts.items():
        corrected_plate_counts[plate] += count
    # print(corrections)
    return corrected_plate_counts, plate_corrections, corrections


def correct_data(df, correction):
    new_df = df
    for c in correction:
        new_df['Plate'].replace(c[0], c[1], regex=False, inplace=True)
    return new_df

# check plate if one digit is different, check make and model to match
# filter buses


def filter_data(df):
    # creating a dictionary
    plate_counts = defaultdict(int)

    # (1) UNIQUE PLATES
    for plate in df['Plate']:
        plate_counts[plate] += 1
    # changing the plate charact/corrections
    corrected_plates, plate_corrections, correction = correct_similar_plates(
        plate_counts, df)

    filter_zero = correct_data(df, correction)
    # print("zero")
    # print(filter_zero.shape[0])
    first_filter_good, first_filter_bad = filter_car_make(filter_zero)
    second_filter_good, second_filter_bad = filter_plate_confidence(
        first_filter_good)
    # print("first")
    # print(first_filter_good.shape[0])
    # print(first_filter_bad.shape[0])
    third_filter_good, third_filter_bad = filter_state(second_filter_good)
    # print("second")
    # print(second_filter_good.shape[0])
    # print(second_filter_bad.shape[0])
    df_comb = pd.concat([second_filter_bad, third_filter_bad])
    fourth_filter_good, fourth_filter_bad = filter_plate_duplicate(df_comb)
    # filter toyota out of it {T0Y0TA, toyota}
    fifth_filter = filter_bus(fourth_filter_good)
    # print("fourth")
    # print(fourth_filter.shape[0])
    return pd.concat([third_filter_good, fifth_filter]), pd.concat([fourth_filter_bad, first_filter_bad])
