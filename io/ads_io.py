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
    Opens an .ads file, reads the data, and returns the data structure.

    :param file_name: *str* The path of the file to read.

    :return: *dict, optional* The parsed data structure if successful, otherwise None.

    :raises ValueError: If the file_path is empty.
    :raises FileNotFoundError: If the specified file does not exist.
    :raises IOError: If there is an error reading or opening the file.

    :examples:
    >>> from fp_dataio.io.ads_io import load_ads_file
    >>> file_name = "J170L07D_Geom_Basic.ads"
    >>> data_struct = load_ads_file(file_name=file_name)
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
        raise FileNotFoundError(f"ads_data.load_ads_file: Error - file does not exist {file_name}") from e
    except IOError as e:
        raise IOError(f"ads_data.load_ads_file: Error - Unable to open or read file: {file_name}") from e

# ===========================================================================
def structure_ads_data(data_lines: List[str]) -> Optional[dict]:
    """
    Generates a nested data structure from a list of ADS-formatted data lines.

    :param data_lines: *List[str]* A list of strings, where each string is a line from the ADS file.

    :return: *dict, optional* The parsed data structure as a nested dictionary and list.

    :examples:
    >>> from fp_dataio.io.ads_io import structure_ads_data
    >>> data_lines = []
    >>> data_dict = structure_ads_data(data_lines=data_lines)
    """
    data_struct = {}



        data_field = data_struct
        (name, sep, value) = line.partition("=")
        value = value.rstrip()
        fields = name.split(".")
        num_fields = len(fields)
        last_field_index = num_fields - 1

        for field_index in range(num_fields):
            field = fields[field_index]

            if "[" in field:  # array element with index
                (array_name, bracket, index_part) = field.partition("[")
                (index_str, bracket, dummy) = index_part.partition("]")
                indices = index_str.split(",")
                num_indices = len(indices)
                last_array_dim = num_indices - 1

                if array_name not in data_field:
                    data_field[array_name] = []
                data_field = data_field[array_name]

                for array_dim in range(num_indices):
                    array_index = int(indices[array_dim])
                    if array_dim < last_array_dim:
                        while array_index > (len(data_field) - 1):
                            data_field.append([])
                        data_field = data_field[array_index]
                    elif array_dim == last_array_dim and field_index < last_field_index:
                        while array_index > (len(data_field) - 1):
                            data_field.append({})
                        data_field = data_field[array_index]
                    elif array_dim == last_array_dim and field_index == last_field_index:
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
                        data_field[field] = value

    return data_struct

# ===========================================================================
