import os
from typing import Optional
from pathlib import Path

import logging

logging.basicConfig(level=logging.INFO)

from fp_dataio.data_models.els_data import ElsData
from fp_dataio.utils.file_rw import File_rw

class ElsDataIo(object):
    """
    Handles reading and writing of ElsData files.
    """

    @staticmethod
    def read_file(file_name: Optional[str | Path]) -> ElsData:
        """
        Opens the file and reads the data into the object data structure using pandas.

        :param file_name: *string* Name of the file.

        :return: ElsData object

        :examples:
        >>> from fp_dataio.io.els_io import ElsDataIo
        >>> filename = "PA43L0M2_ELS-05.csv"
        >>> els_obj = ElsDataIo.read_file(file_name=filename)
        >>> els_obj.has_iq("IQ_name")
        """
        # -----------------------------------------------------------------------
        # check file name
        if not file_name:
            raise ValueError("els_data.read_file: Error - Empty file name")

        # check file existence
        if not os.path.exists(file_name):
            raise FileNotFoundError(f"els_data.read_file: Error - File not found {file_name}")

        # -----------------------------------------------------------------------
        try:
            file_obj = open(file_name, "r", encoding="latin-1")
        except IOError:
            raise ("els_data.read_file: Error - Unable to open file: %s" % file_name)


        file_line = file_obj.readlines()

        file_obj.close()
        file_obj= None

        headline = file_line.pop(0)

        els_obj = ElsData(file_name=file_name)
        els_obj.set_csv_data(file_line)

        return els_obj
    # ===========================================================================

    @staticmethod
    def write_file(file_name: Optional[str | Path], els_data_obj: ElsData):
        """
        write the data from memory into an (csv) file

        :param file_name: *string* file name
        :param els_data_obj: *ElsData* els_data object

        :return: *int* Returns 1 on success and None on failure.

        :examples:
        >>> from fp_dataio.io.els_io import ElsDataIo
        >>> filename = "PA43L0M2_ELS-05.csv"
        >>> els_obj = ElsDataIo.read_file(file_name=filename)
        >>> els_obj.has_iq("IQ_name")
        >>> writefile = "filename.csv"
        >>> ElsDataIo.write_file(file_name=writefile,els_data_obj=els_obj)
        """
        # -----------------------------------------------------------------------
        # open file
        if not file_name:
            raise ValueError("els_data_io.write_file: Error - Empty file name")

        file_obj = File_rw(file_name, "w")

        # -----------------------------------------------------------------------
        # write header line
        headline = ",".join(ElsData.ELS_column_names)
        file_obj.write_line(headline)

        # write data lines
        for IQ_name in sorted(els_data_obj.IQ_names):
            csv_line = els_data_obj.get_csv_line(IQ_name)
            file_obj.write_line(csv_line)

        # -----------------------------------------------------------------------
        # close the file
        file_obj.close()
        file_obj = None

        logging.info(f"File {file_name} written successfully.")
# ===========================================================================