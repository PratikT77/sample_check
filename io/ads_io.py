"""
Functions for the access to ADS format files.
"""
################################################################################
from typing import List, Optional
from fp_dataio.utils.data_struct_func import *

################################################################################
# global variables

comment_char = "#"

################################################################################
def load_ads_file(file_name: str) -> Optional[dict]:
    """
    Opens an ads file, reads the data and returns the data structure

    Args:
        file_name (str): The Path of the file to read

    Returns:
        Optional[dict]: The parsed data structure if successful, otherwise None

    Raises:
        ValueError: if the file_path is empty.
        FileNotFoundError: if the specific file does not exist
        IOError: if there is an error reading or opening the file
    """

    # check file path
    if not file_name:
        raise ValueError("ads_data.load_ads_file: Error - Empty file path")

    try:
        with open(file_name, "r", encoding="latin-1") as file_obj:
            file_lines = file_obj.readlines()

        data_struct = structure_ads_data(file_lines)

        return data_struct
    except FileNotFoundError as e:
        raise FileNotFoundError(f"ads_data.load_ads_file: Error - file does not exist {file_name}")
    except IOError as e:
        raise IOError(f"ads_data.load_ads_file: Error - Unable to open or read file: {file_name}") from e

# ===========================================================================
def structure_ads_data(data_lines) -> Optional[dict]:
    """
    Generates a nested data structure from a list of ADS-formatted data lines.

    This function parses each line, splitting keys and values, and builds a
    complex structure of nested dictionaries and lists based on '.' and '[]'
    notation in the keys.

    Args:
        data_lines (List[str]): A list of strings, where each string is a
                                line from the ADS file.

    Returns:
        Optional[dict]: The parsed data structure as a nested dictionary and
                        list. Returns an empty dictionary if data_lines is empty.
    """
    data_struct = {}

    line_number = 0

    for line in data_lines:
        line_number += 1

        # print ("Line (%s): %s" % (line_number,line))

        if not line:
            continue

        if line.startswith(comment_char):
            continue

        data_field = (
            data_struct  # pointer to the current field within the data structure
        )

        (name, sep, value) = line.partition("=")
        value = value.rstrip()
        fields = name.split(".")
        num_fields = len(fields)
        last_field_index = num_fields - 1

        for field_index in range(0, num_fields):
            field = fields[field_index]

            # print ("Field: %s" % field)

            if "[" in field:  # array element with index
                (array_name, bracket, index_part) = field.partition("[")
                (index_str, bracket, dummy) = index_part.partition("]")
                indices = index_str.split(",")
                num_indices = len(indices)
                last_array_dim = num_indices - 1

                if array_name not in data_field:
                    data_field[array_name] = []

                data_field = data_field[array_name]

                for array_dim in range(0, num_indices):
                    array_index = int(indices[array_dim])

                    if array_dim < last_array_dim:
                        while array_index > (len(data_field) - 1):
                            data_field.append([])

                        data_field = data_field[array_index]

                    elif array_dim == last_array_dim and field_index < last_field_index:
                        while array_index > (len(data_field) - 1):
                            data_field.append({})

                        data_field = data_field[array_index]

                    elif (
                            array_dim == last_array_dim and field_index == last_field_index
                    ):
                        while array_index > (len(data_field) - 1):
                            data_field.append(None)

                        data_field[array_index] = value

            else:  # hash/dict key
                if field in data_field:
                    data_field = data_field[field]

                else:
                    if field_index < last_field_index:
                        data_field[field] = {}

                        data_field = data_field[field]

                    else:
                        # print ("Value = %s" % (value))

                        data_field[field] = value

    # -----------------------------------------------------------------------
    # return the data structure

    return data_struct

# ===========================================================================
def save_ads_file(file_name, data_name, data_struct):
    """
    Saves a data structure into an ads file.

    Args:
        file_name (str): The name of the file to save the data to.
        data_name (str): The name of the data being saved.
        data_struct (Any): The data structure to save

    Returns:
        Optional[int]: 1 if successful, None if an error occurs

    Raises:
        ValueError: if the file name is empty.
        IOError: if there is an error opening or writing to the file
    """

    if not file_name:
        raise ValueError("ads_data.save_ads_file: Error - Empty file name")

    try:
        with open(file_name, "w", encoding="latin-1") as file_obj:
            print_data_struct(data_name, data_struct, file_obj)

        return 1
    except FileNotFoundError as e:
        raise FileNotFoundError(f"ads_data.save_ads_file: Error - file does not exist {file_name}")
    except IOError as e:
        raise IOError(f"ads_data.save_ads_file: Error - Unable to open or write to file: {file_name}") from e
