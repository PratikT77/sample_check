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
    def read_file(file_name: Optional[str | Path])-> GeomBasicData:
        """
        Opens and reads the component data from a .ads file.

        :param file_name: *str or Path* The path to the .ads file.

        :return: *GeomBasicData* A GeomBasicData object with the loaded data.

        :raises ValueError: If the file data does not contain "Basic".

        :examples:
            >>> from fp_dataio.io.geom_basic_io import GeomBasicIo
            >>> filename = r"PA43L0M2_Geom_Basic.ads"
            >>> geom_obj = GeomBasicIo.read_file(file_name=filename)
            >>> geom_obj.get_ads_data()
        """

        file_data = load_ads_file(file_name)

        if not "Basic" in file_data:
            raise ValueError(f"geom_basic_io.read_file: Error - not a valid GEOM_Basic file: {file_name}")

        geom_basic_obj = GeomBasicData(file_name=file_name)
        geom_basic_obj.data = file_data["Basic"]


        return geom_basic_obj


    # ===========================================================================

    @staticmethod
    def write_file(file_name: Optional[str | Path], data: dict[str, Any]):
        """
        Writes the data from memory into a .ads file.

        :param file_name: *str or Path* The path to the file to be written.
        :param data: *dict* Data dictionary from the geom_basic_data.data.

        :examples:
            >>> from fp_dataio.io.geom_basic_io import GeomBasicIo
            >>> filename = "PA43L0M2_Geom_Basic.ads"
            >>> geom_obj = GeomBasicIo.read_file(filename)
            >>> writefile = r"xyz.ads"
            >>> GeomBasicIo.write_file(file_name=writefile, data=geom_obj.data)
        """
        save_ads_file(file_name, "Basic.", data)

        logging.info(f"File {file_name} written successfully.")

################################################################################