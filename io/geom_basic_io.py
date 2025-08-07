import logging

logging.basicConfig(level=logging.INFO)
from pathlib import Path

from typing import Any, Optional

from fp_dataio.data_models.geom_basic_data import GeomBasicData
from fp_dataio.io.ads_io import load_ads_file,save_ads_file

class GeomBasicIo(object):
    """
    Handles reading and writing of GeomBasicIo files.
    """


    @staticmethod
    def read_file(file_name: Union[str | Path]) -> GeomOsData:
        """
        opens the file and reads the data into the object data structure

        Args:
            file_name (str): file path

        Example:
            >>> from fp_dataio.io.geom_os_io import GeomOsIo
            >>> filename = r"PA43L0M2_Geom_OS.ads"
            >>> geom_obj = GeomOsIo.read_file(filename)
            >>> print(geom_obj.comp_stations.keys())
        """
        file_data = load_ads_file(file_name)

        if not "Output_Stations" in file_data:
            raise ValueError(f"geom_os_data.read_file: Error - not a valid GEOM_OS file {file_name}")

        geom_os_obj = GeomOsData(file_name=file_name)
        geom_os_obj.os_data = file_data["Output_Stations"]

        # -----------------------------------------------------------------------
        # generate the station_data structure

        geom_os_obj.set_station_data()

        return geom_os_obj

    # ===========================================================================

    @staticmethod
    def write_file(file_name: Union[str | Path], geom_os_obj: GeomOsData) -> bool:
        """
        Writes the current data from memory into an ADS-formatted file.

        Args:
            file_name (str): The name of the file to write the data to.
            geom_os_obj (GeomOsData): GeomOSData object

        Returns:
            Optional[bool]: True if the file was written successfully,
                            False if an error occurred during writing,

        Raise:
            ValueError: If the File Name is empty

        Example:
            >>> from fp_dataio.io.geom_os_io import GeomOsIo
            >>> filename = r"PA43L0M2_Geom_OS.ads"
            >>> geom_obj = GeomOsIo.read_file(file_name=filename)
            >>> writefile = "xyz.ads"
            >>> success = GeomOsIo.write_file(file_name=writefile,geom_os_obj=geom_obj)
        """
        if not file_name:
            raise ValueError(f"geom_os_data Error: Empty file path {file_name}")

        # -----------------------------------------------------------------------
        # update the self.os_data with the station objects data

        comp_list = geom_os_obj.os_data["Stations"].keys()

        for comp in comp_list:
            comp_os_data = geom_os_obj.os_data["Stations"][comp]
            comp_key = comp_os_data["Component"]["Comp_Key"]

            if comp_key in geom_os_obj.comp_stations:
                comp_os_data["Stations"] = []

                for station_obj in geom_os_obj.comp_stations[comp_key]:
                    station_os_data = {}
                    station_os_data["Station_ID"] = station_obj.Station_ID
                    station_os_data[
                        "Station_Description"
                    ] = station_obj.Station_Description
                    station_os_data["Coordinates"] = station_obj.Coordinates
                    station_os_data["Reference_COS_ID"] = 1

                    comp_os_data["Stations"].append(station_os_data)
            else:
                if "Stations" in comp_os_data:
                    del comp_os_data["Stations"]

        # -----------------------------------------------------------------------

        try:
            save_ads_file(file_name, "Output_Stations.", geom_os_obj.os_data)
            return True
        except Exception as e:
            logging.warning(f"geom_os_data.write_file: Error writing file '{file_name}': {e}")
            return False################################################################################