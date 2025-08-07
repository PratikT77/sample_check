# -*- coding: latin-1 -*-

"""
ELS data methods
"""
################################################################################
import os
# from .file_rw import File_rw

# from fp_dataio import Utility_function
from fp_dataio.Utility_function.file_rw import File_rw

################################################################################
# global variables

axis_index = {"x": 0, "y": 1, "z": 2}


################################################################################
class ELS_data(object):
    """
    ELS data methods
    """

    ELS_column_names = [
        "IQ_name",
        "Component_Key",
        "Component_Name",
        "Station",
        "Station_Type",
        "CID",
        "Rotation_flag",
        "DOF",
        "IQ_Type",
        "IQ_Qual",
        "SISO",
        "ISO",
        "IQ_Description",
        "Unit",
        "Conversion_factor",
        "Skill_Mark",
        "Mirror_flag",
        "Selection_flag",
        "DB_flag",
        "Keyword",
        "Formula",
        "Comment",
    ]

    IQ_attr_names = [
        "name",
        "comp_key",
        "comp_name",
        "station",
        "station_id",
        "station_type",
        "station_desc",
        "station_index",
        "station_obj",
        "CID",
        "rotation_flag",
        "DOF",
        "load_type",
        "qualifier",
        "SISO",
        "ISO",
        "type",
        "unit",
        "factor",
        "skill_mark",
        "mirror_flag",
        "sel_flag",
        "DB_flag",
        "keyword",
        "formula",
        "comment",
        "index",
        "coord_axis",
        "coord",
        "plf2d_name",
    ]

    IQ_attr_names_set = set(IQ_attr_names)

    ELS_column_to_IQ_attr_name_mapping = {
        "IQ_name": "name",
        "Component_Key": "comp_key",
        "Component_Name": "comp_name",
        "Station": "station",
        "Station_Type": "station_type",
        "CID": "CID",
        "Rotation_flag": "rotation_flag",
        "DOF": "DOF",
        "IQ_Type": "load_type",
        "IQ_Qual": "qualifier",
        "SISO": "SISO",
        "ISO": "ISO",
        "IQ_Description": "type",
        "Unit": "unit",
        "Conversion_factor": "factor",
        "Skill_Mark": "skill_mark",
        "Mirror_flag": "mirror_flag",
        "Selection_flag": "sel_flag",
        "DB_flag": "DB_flag",
        "Keyword": "keyword",
        "Formula": "formula",
        "Comment": "comment",
    }

    ind_col_station = ELS_column_names.index("Station")
    ind_col_ISO = ELS_column_names.index("ISO")

    # ===========================================================================
    def __init__(self, file_name=None):
        """
        Constructor
        """
        self.init_data()

        if file_name is not None and os.path.exists(file_name):
            self.read_file(file_name)

    # ===========================================================================
    def __repr__(self):
        """
        String conversion
        """
        return "ELS_data: %s" % self.file_name

    # ===========================================================================
    def init_data(self):
        """
        Initializes the data members of the class ELS_data

        :param self: *object* ELS_data object.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> a.init_data()
        """
        self.file_name = None

        self.info = {}

        self.IQ_names = []
        self.IQ_name_set = set()
        self.IQ_data = {}
        self.AC_param = {}
        self.CQ_dict = {}
        self.plot_data1 = {}
        self.plot_data2 = {}

        self.geom_basic_obj = None
        self.geom_os_obj = None

    # ===========================================================================
    def read_file(self, file_name):
        """
        opens the file and reads the data into the object data structure

        :param self: *object* ELS_data object.
        :param file_name: *string* Name of the file.

        :return: *int or None* Returns "1" on success and "None" on failure

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> out = a.read_file("fileName.csv")
        """
        # -----------------------------------------------------------------------
        # check file name

        if not file_name:
            print("els_data.read_file: Error - Empty file name")
            return None

        # check file existance
        if not os.path.exists(file_name):
            print("els_data.read_file: Error - File not found %s" % file_name)
            return None

        # -----------------------------------------------------------------------
        # open file and read content

        try:
            file_obj = open(file_name, "r", encoding="latin-1")
        except IOError:
            print("els_data.read_file: Error - Unable to open file: %s" % file_name)
            return None

        # read all lines of the file
        file_lines = file_obj.readlines()

        # close the file
        file_obj.close()
        file_obj = None

        # -----------------------------------------------------------------------
        # analyze the file content and generate the data structure

        headline = file_lines.pop(0)

        self.set_csv_data(file_lines)

        # -----------------------------------------------------------------------

        self.file_name = file_name

        return 1  # success value

    # ===========================================================================
    def set_csv_data(self, csv_lines):
        """
        processes the csv data into the object data structure

        :param self: *object* ELS_data object.
        :param csv_lines: *list* CSV data to process.

        :return: *None*

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> file_obj = open(file_name, "r", encoding="latin-1") //open file
        >>> file_lines = file_obj.readlines() //read lines
        >>> file_obj.close()
        >>> a.set_csv_data(file_lines)
        """
        self.init_data()

        n_ELS_columns = len(ELS_data.ELS_column_names)

        for line in csv_lines:
            line = line.rstrip()  # remove trailing whitespaces

            if not line:
                continue  # skip empty lines

            fields = line.split(",")

            if len(fields) < n_ELS_columns:
                n_missing_fields = n_ELS_columns - len(fields)
                fields += [""] * n_missing_fields

            elif len(fields) > n_ELS_columns:
                fields = fields[:n_ELS_columns]

            IQ = self.add_IQ(dict(zip(ELS_data.ELS_column_names, fields)))

    # ===========================================================================
    def add_IQ(self, IQ_def_dict):
        """
        add a new IQ to the IQ data

        :param self: *object* ELS_data object.
        :param IQ_def_dict: *dict* New IQ data to add.

        :return: *object* Returns IQ data object

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> IQ = a.add_IQ(dict(iq_data))
        """
        # -----------------------------------------------------------------------

        if not "name" in IQ_def_dict and not "IQ_name" in IQ_def_dict:
            print("ELS Data error: IQ definition without IQ name:", IQ_def_dict)
            return None

        if "name" in IQ_def_dict:
            IQ_name = IQ_def_dict["name"]
        if "IQ_name" in IQ_def_dict:
            IQ_name = IQ_def_dict["IQ_name"]

        if IQ_name in self.IQ_name_set:
            print("ELS Data error: IQ name duplication:  ", IQ_name)

            count = 2
            while IQ_name in self.IQ_name_set:
                IQ_name = IQ_name + "_%s" % count
                count += 1

            print("                IQ name modified into:", IQ_name)
            IQ_def_dict["IQ_name"] = IQ_name
            if "name" in IQ_def_dict:
                del IQ_def_dict["name"]

            print(
                "IQ definition: Comp=%s, Station=%s, ISO=%s, Type=%s, Unit=%s"
                % (
                    IQ_def_dict["comp_key"],
                    IQ_def_dict["station"],
                    IQ_def_dict["ISO"],
                    IQ_def_dict["type"],
                    IQ_def_dict["unit"],
                )
            )

        # -----------------------------------------------------------------------

        IQ = IQ_def(IQ_def_dict)

        self.IQ_names.append(IQ.name)
        self.IQ_name_set.add(IQ.name)
        self.IQ_data[IQ.name] = IQ

        if IQ.index is None:
            IQ_index = len(self.IQ_names) - 1
            IQ.set_attribute("index", IQ_index)

        # print ("New IQ: %s [%s]" % (IQ.name,IQ.index))
        # print ("New IQ %s => %s = %s" % (IQ.name,IQ.coord_axis,IQ.coord))

        # -----------------------------------------------------------------------

        if IQ.comp_key == "AC":
            self.AC_param[IQ.name] = IQ
            if int(IQ.station_id) > 1 and IQ.ISO == 1:
                IQ.ISO = int(IQ.station_id)
            IQ.station_id = "1"
            IQ.station = IQ.comp_key + "." + IQ.station_id
            if IQ.type is None:
                print("Wrong IQ def: %s (%s)" % (IQ.name, IQ.type))

            # print ("New AC_param: %s (%s)" % (IQ.name,IQ.type))

        # -----------------------------------------------------------------------

        if IQ.comp_key == "CQ" and ":" in IQ.formula:
            IQ1_str, dummy, IQ2_str = IQ.formula.partition(":")
            IQ1_name = IQ1_str.strip()
            if IQ1_name.startswith("$"):
                IQ1_name = IQ1_name[1:]
            if IQ1_name.startswith("{"):
                IQ1_name = IQ1_name[1:]
            if IQ1_name.endswith("}"):
                IQ1_name = IQ1_name[:-1]
            IQ2_name = IQ2_str.strip()
            if IQ2_name.startswith("$"):
                IQ2_name = IQ2_name[1:]
            if IQ2_name.startswith("{"):
                IQ2_name = IQ2_name[1:]
            if IQ2_name.endswith("}"):
                IQ2_name = IQ2_name[:-1]

            if IQ1_name not in self.CQ_dict:
                self.CQ_dict[IQ1_name] = {}

            if IQ2_name not in self.CQ_dict[IQ1_name]:
                self.CQ_dict[IQ1_name][IQ2_name] = 1

        # -----------------------------------------------------------------------

        if not IQ.comp_key in self.plot_data1:
            self.plot_data1[IQ.comp_key] = {}

        if not IQ.type in self.plot_data1[IQ.comp_key]:
            self.plot_data1[IQ.comp_key][IQ.type] = {}

            self.plot_data1[IQ.comp_key][IQ.type]["coord_axis"] = IQ.coord_axis
            self.plot_data1[IQ.comp_key][IQ.type]["ISO"] = IQ.ISO
            self.plot_data1[IQ.comp_key][IQ.type]["IQ_type"] = IQ.type
            self.plot_data1[IQ.comp_key][IQ.type]["IQ_unit"] = IQ.unit
            self.plot_data1[IQ.comp_key][IQ.type]["IQ_list"] = []
            self.plot_data1[IQ.comp_key][IQ.type]["IQ_names"] = []
            self.plot_data1[IQ.comp_key][IQ.type]["IQ_factors"] = []
            self.plot_data1[IQ.comp_key][IQ.type]["IQ_stations"] = []
            self.plot_data1[IQ.comp_key][IQ.type]["IQ_stations_desc"] = []
            self.plot_data1[IQ.comp_key][IQ.type]["IQ_coords"] = []

        self.plot_data1[IQ.comp_key][IQ.type]["IQ_list"].append(IQ)
        self.plot_data1[IQ.comp_key][IQ.type]["IQ_names"].append(IQ.name)
        self.plot_data1[IQ.comp_key][IQ.type]["IQ_factors"].append(IQ.factor)
        self.plot_data1[IQ.comp_key][IQ.type]["IQ_stations"].append(IQ.station)
        self.plot_data1[IQ.comp_key][IQ.type]["IQ_stations_desc"].append(
            IQ.station_desc
        )
        self.plot_data1[IQ.comp_key][IQ.type]["IQ_coords"].append(IQ.coord)

        # -----------------------------------------------------------------------

        if not IQ.comp_key in self.plot_data2:
            self.plot_data2[IQ.comp_key] = {}

        if not IQ.ISO in self.plot_data2[IQ.comp_key]:
            self.plot_data2[IQ.comp_key][IQ.ISO] = {}

            self.plot_data2[IQ.comp_key][IQ.ISO]["coord_axis"] = IQ.coord_axis
            self.plot_data2[IQ.comp_key][IQ.ISO]["ISO"] = IQ.ISO
            self.plot_data2[IQ.comp_key][IQ.ISO]["IQ_type"] = IQ.type
            self.plot_data2[IQ.comp_key][IQ.ISO]["IQ_unit"] = IQ.unit
            self.plot_data2[IQ.comp_key][IQ.ISO]["IQ_list"] = []
            self.plot_data2[IQ.comp_key][IQ.ISO]["IQ_names"] = []
            self.plot_data2[IQ.comp_key][IQ.ISO]["IQ_factors"] = []
            self.plot_data2[IQ.comp_key][IQ.ISO]["IQ_stations"] = []
            self.plot_data2[IQ.comp_key][IQ.ISO]["IQ_stations_desc"] = []
            self.plot_data2[IQ.comp_key][IQ.ISO]["IQ_coords"] = []

        self.plot_data2[IQ.comp_key][IQ.ISO]["IQ_list"].append(IQ)
        self.plot_data2[IQ.comp_key][IQ.ISO]["IQ_names"].append(IQ.name)
        self.plot_data2[IQ.comp_key][IQ.ISO]["IQ_factors"].append(IQ.factor)
        self.plot_data2[IQ.comp_key][IQ.ISO]["IQ_stations"].append(IQ.station)
        self.plot_data2[IQ.comp_key][IQ.ISO]["IQ_stations_desc"].append(IQ.station_desc)
        self.plot_data2[IQ.comp_key][IQ.ISO]["IQ_coords"].append(IQ.coord)

        # -----------------------------------------------------------------------

        return IQ

    # ===========================================================================
    def get_expanded_IQs(self):
        """
        returns a list with the expanded IQ names
        """
        # Initialize list of expanded IQs
        expanded_IQs = []

        # Loop over ELS IQ names
        for IQ1_name in self.IQ_names:
            IQ1_obj = self.IQ_data[IQ1_name]
            # Check if IQ is CO or LC and the qualifier is **
            if IQ1_obj.load_type.strip() in ['CO', 'LC'] and IQ1_obj.qualifier.strip() == '**':
                formula = IQ1_obj.formula.strip()  # remove leading + trailing blanks
                formula = "".join(formula.split()).strip()  # remove internal blanks
                # Check if formula is not empty
                if len(formula) > 0:
                    expanded_IQs.append([IQ1_name, formula.replace('${', '{')])

        return expanded_IQs

    # ===========================================================================

    def get_basic_IQs(self):
        """
        Checks whether the LRC is already mirrored or is extended
        :return:
        """
        # Filter out mirrored and extended
        basic_iqs = []
        mirr_formulas = {}
        for IQ1_name in self.IQ_names:

            IQ1_obj = self.IQ_data[IQ1_name]
            # Do not process expanded IQs
            if IQ1_obj.load_type.strip() in ['CO', 'LC'] and IQ1_obj.qualifier.strip() == '**':
                continue

            if IQ1_obj.mirror_flag:
                mirr_formula = IQ1_obj.formula.strip()  # remove leading + trailing blanks
                mirr_formula = "".join(mirr_formula.split())  # remove internal blanks
                mirr_formulas[IQ1_name] = mirr_formula

                basic_iqs.append(IQ1_name)

        return basic_iqs, mirr_formulas

    ################################################################################

    # ===========================================================================
    def delete_IQ(self, IQ_name):
        """
        deletes an IQ

        :param self: *object* ELS_data object.
        :param IQ_def_dict: *string* IQ data to delete.

        :return: *bool* Returns True on success.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> retVal = a.delete_IQ("name")
        """
        # -----------------------------------------------------------------------

        # print ("els_data.delete_IQ: IQ name: %s" % IQ_name)

        if IQ_name not in self.IQ_data:
            print("els_data.delete_IQ: invalid IQ name: %s" % IQ_name)
            return None

        IQ = self.IQ_data[IQ_name]

        ind_IQ = self.plot_data1[IQ.comp_key][IQ.type]["IQ_names"].index(IQ_name)

        self.plot_data1[IQ.comp_key][IQ.type]["IQ_list"].pop(ind_IQ)
        self.plot_data1[IQ.comp_key][IQ.type]["IQ_names"].pop(ind_IQ)
        self.plot_data1[IQ.comp_key][IQ.type]["IQ_factors"].pop(ind_IQ)
        self.plot_data1[IQ.comp_key][IQ.type]["IQ_stations"].pop(ind_IQ)
        self.plot_data1[IQ.comp_key][IQ.type]["IQ_stations_desc"].pop(ind_IQ)
        self.plot_data1[IQ.comp_key][IQ.type]["IQ_coords"].pop(ind_IQ)

        for index, IQ1 in enumerate(self.plot_data1[IQ.comp_key][IQ.type]["IQ_list"]):
            IQ1.index = index

        ind_IQ = self.plot_data2[IQ.comp_key][IQ.ISO]["IQ_names"].index(IQ_name)

        self.plot_data2[IQ.comp_key][IQ.ISO]["IQ_list"].pop(ind_IQ)
        self.plot_data2[IQ.comp_key][IQ.ISO]["IQ_names"].pop(ind_IQ)
        self.plot_data2[IQ.comp_key][IQ.ISO]["IQ_factors"].pop(ind_IQ)
        self.plot_data2[IQ.comp_key][IQ.ISO]["IQ_stations"].pop(ind_IQ)
        self.plot_data2[IQ.comp_key][IQ.ISO]["IQ_stations_desc"].pop(ind_IQ)
        self.plot_data2[IQ.comp_key][IQ.ISO]["IQ_coords"].pop(ind_IQ)

        for index, IQ2 in enumerate(self.plot_data2[IQ.comp_key][IQ.ISO]["IQ_list"]):
            IQ2.index = index

        del self.IQ_data[IQ_name]

        self.IQ_names.remove(IQ_name)

        return True

    # ===========================================================================
    def set_geom_model(self, geom_basic_obj, geom_os_obj):
        """
        sets the references to the related GEOM_Basic and GEOM_OS data objects

        :param self: *object* ELS_data class object.
        :param geom_basic_obj: *object* GEOM_Basic_data class object.
        :param geom_os_obj: *object* GEOM_OS_data class object.

        :return: *dict* Returns error_data and if there are no error_data returns None.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> geom_basic_obj = GEOM_Basic_data()
        >>> geom_os_obj = GEOM_OS_data()
        >>> error_data = a.set_geom_model(geom_basic_obj, geom_os_obj)
        """
        # -----------------------------------------------------------------------

        self.geom_basic_obj = geom_basic_obj
        self.geom_os_obj = geom_os_obj

        self.init_error_data()

        error_data = self.check_data_consistency()

        self.set_station_ref()

        self.sort_plot_data()

        return error_data

    # ===========================================================================
    def init_error_data(self):
        """
        Initializes error data

        :param self: *object* ELS_data class object.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> a.init_error_data()
        """
        # -----------------------------------------------------------------------

        self.error_data = {
            "error_count": 0,
            "missing_components": [],
            "missing_stations": [],
        }

    # ===========================================================================
    def check_data_consistency(self):
        """
        check the consistency of components and output stations with IQs

        :param self: *object* ELS_data class object.

        :return: *dict* Returns error_data and if there are no error_data returns None.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> error_data = a.check_data_consistency()
        """
        # -----------------------------------------------------------------------

        if self.geom_basic_obj is None:
            print("check_data_consistency: no GEOM_model is set for %s" % self)
            return
        if self.geom_os_obj is None:
            print("check_data_consistency: no GEOM_model is set for %s" % self)
            return

        # -----------------------------------------------------------------------
        # check for missing component definitions

        for comp_key in self.plot_data1.keys():
            if comp_key != "CQ" and (not self.geom_basic_obj.has_component(comp_key)):
                if not comp_key in self.error_data["missing_components"]:
                    self.error_data["error_count"] += 1
                    self.error_data["missing_components"].append(comp_key)

        # -----------------------------------------------------------------------
        # check for missing output stations

        removal_list = []

        for IQ_name in self.IQ_names:
            IQ_station = self.IQ_data[IQ_name].station
            comp_key = self.IQ_data[IQ_name].comp_key
            station_type = self.IQ_data[IQ_name].station_type

            # print ("check_data_consistency IQ: %s [%s] (%s)" % (IQ_name,IQ_station,station_type))

            if comp_key != "CQ" and (not self.geom_basic_obj.has_component(comp_key)):
                if not IQ_name in removal_list:
                    removal_list.append(IQ_name)
                if not comp_key in self.error_data["missing_components"]:
                    self.error_data["error_count"] += 1
                    self.error_data["missing_components"].append(comp_key)

            if station_type == "g" and (not self.geom_os_obj.has_station(IQ_station)):
                if not IQ_name in removal_list:
                    removal_list.append(IQ_name)
                if not IQ_station in self.error_data["missing_stations"]:
                    self.error_data["error_count"] += 1
                    self.error_data["missing_stations"].append(IQ_station)

        for IQ_name in removal_list:
            self.delete_IQ(IQ_name)

        # -----------------------------------------------------------------------

        if self.error_data["error_count"] > 0:
            return self.error_data
        else:
            return None

    # ===========================================================================
    def set_station_ref(self):
        """
        checks the GEOM_OS for the corresponding station and sets the reference

        :param self: *object* ELS_data class object.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> a.set_station_ref()
        """
        # -----------------------------------------------------------------------

        for IQ_name in self.IQ_names:
            IQ = self.IQ_data[IQ_name]

            if IQ.coord_axis is None or IQ.coord_axis == "":
                IQ.coord_axis = self.geom_basic_obj.get_component_integration_axis(
                    IQ.comp_key
                )   # related with the geom_basic

            if IQ.station_obj is None and IQ.station:
                IQ.station_obj = self.geom_os_obj.get_station(IQ.station)

                if IQ.station_obj is None:
                    # print ("No station found for %s (%s)" % (IQ.name,IQ.station))
                    continue

                IQ.station_desc = IQ.station_obj.Station_Description

                if IQ.coord is None and IQ.coord_axis:
                    iaxis = axis_index[IQ.coord_axis]
                    IQ.coord = IQ.station_obj.Coordinates[iaxis]

    # ===========================================================================
    def sort_plot_data(self):
        """
        sorts the IQ lists for each component and IQ type by the coordinate values

        :param self: *object* ELS_data class object.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> geom_basic_obj = GEOM_Basic_data()
        >>> geom_os_obj = GEOM_OS_data()
        >>> error_data = a.sort_plot_data()
        """
        # -----------------------------------------------------------------------

        if self.geom_basic_obj is None:
            print("sort_plot_data: no GEOM_model is set for %s" % self)
            return
        if self.geom_os_obj is None:
            print("sort_plot_data: no GEOM_model is set for %s" % self)
            return

        # -----------------------------------------------------------------------

        self.sort_plot_data1()
        self.sort_plot_data2()

    # ===========================================================================
    def sort_plot_data1(self):
        """
        sorts the IQ lists for each component and IQ type by the coordinate values

        :param self: *object* ELS_data class object.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> geom_basic_obj = GEOM_Basic_data()
        >>> geom_os_obj = GEOM_OS_data()
        >>> error_data = a.sort_plot_data1()
        """
        # -----------------------------------------------------------------------

        remove_list = []

        for comp_key in self.plot_data1:
            for IQ_type in self.plot_data1[comp_key]:
                self.sort_IQ_list(self.plot_data1, comp_key, IQ_type)

            if not self.geom_basic_obj.has_component(comp_key):
                remove_list.append(comp_key)

        # for comp_key in remove_list:
        #    del self.plot_data1 [comp_key]

    # ===========================================================================
    def sort_plot_data2(self):
        """
        sorts the IQ lists for each component and IQ type by the coordinate values

        :param self: *object* ELS_data class object.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> geom_basic_obj = GEOM_Basic_data()
        >>> geom_os_obj = GEOM_OS_data()
        >>> error_data = a.sort_plot_data2()
        """
        # -----------------------------------------------------------------------

        remove_list = []

        for comp_key in self.plot_data2:
            for IQ_type in self.plot_data2[comp_key]:
                self.sort_IQ_list(self.plot_data2, comp_key, IQ_type)

            if not self.geom_basic_obj.has_component(comp_key):
                remove_list.append(comp_key)

        # for comp_key in remove_list:
        #    del self.plot_data2 [comp_key]

    # ===========================================================================
    def sort_IQ_list(self, plot_data, comp_key, IQ_type):
        """
        sorts the list of IQs for a component and IQ type by the coordinate values

        :param self: *object* ELS_data class object.
        :param plot_data: *dict* plot data with the list of IQs.
        :param comp_key: *string* component key.
        :param IQ_type: *string* IQ type.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> a.read_file("file_name")
        >>> a.sort_IQ_list()
        """
        # -----------------------------------------------------------------------

        IQ_list = plot_data[comp_key][IQ_type]["IQ_list"]

        # print ("sort_IQ_list: %s -> %s: %s" % (comp_key,IQ_type,IQ_list))

        if self.geom_basic_obj.has_component(comp_key):
            sort_axis = self.geom_basic_obj.get_component_integration_axis(comp_key)

            if sort_axis is not None and sort_axis != "":
                plot_data[comp_key][IQ_type]["coord_axis"] = sort_axis

                if not any(IQ.coord is None for IQ in IQ_list):
                    IQ_list.sort(key=lambda iq: (iq.coord))

        # -----------------------------------------------------------------------

        IQ_names = []
        IQ_factors = []
        IQ_stations = []
        IQ_stations_desc = []
        IQ_coords = []

        for ind, IQ in enumerate(IQ_list):
            IQ_names.append(IQ.name)
            IQ_factors.append(IQ.factor)
            IQ_stations.append(IQ.station)
            IQ_stations_desc.append(IQ.station_desc)
            IQ_coords.append(IQ.coord)

            IQ.station_index = ind + 1

            # print ("[%s] %s => %s = %s" % (IQ.station_index,IQ.name,sort_axis,IQ.coord))

        plot_data[comp_key][IQ_type]["IQ_list"] = IQ_list
        plot_data[comp_key][IQ_type]["IQ_names"] = IQ_names
        plot_data[comp_key][IQ_type]["IQ_factors"] = IQ_factors
        plot_data[comp_key][IQ_type]["IQ_stations"] = IQ_stations
        plot_data[comp_key][IQ_type]["IQ_stations_desc"] = IQ_stations_desc
        plot_data[comp_key][IQ_type]["IQ_coords"] = IQ_coords

    # ===========================================================================
    def update_from_station_def(self, station_obj):
        """
        synchronize the IQ data with corresponding station data

        :param self: *object* ELS_data class object.
        :param station_obj: *object* station object.

        :return: *int* Returns total number of IQs modified to syncronize the IQ data.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> station_data = {}
        >>> station_obj = station_data["station_ref"]
        >>> num = a.update_from_station_def(station_obj)
        """
        # -----------------------------------------------------------------------

        n_IQs_modified = 0

        for IQ_name in self.IQ_names:
            IQ = self.IQ_data[IQ_name]

            if IQ.station_obj is None:
                continue
            if IQ.station_obj != station_obj:
                continue

            n_IQs_modified += 1

            IQ_old_name = IQ.name
            station_id = int(IQ.station_obj.Station_ID)

            IQ_new_name = "%s.%04d.%02d" % (IQ.comp_key, station_id, IQ.ISO)

            IQ.name = IQ_new_name
            IQ.station = IQ.station_obj.name
            IQ.station_id = IQ.station_obj.Station_ID
            IQ.station_desc = IQ.station_obj.Station_Description
            iaxis = axis_index[IQ.coord_axis]
            IQ.coord = IQ.station_obj.Coordinates[iaxis]

            # print ("IQ updated: %s -> %s (%s, %s)" % (IQ_old_name,IQ.name,IQ.coord,IQ.station_desc))

        return n_IQs_modified

    # ===========================================================================
    def update_from_station_coords(self, comp_key=None):
        """
        synchronize the IQ data with corresponding station coordinates

        :param self: *object* ELS_data class object.
        :param comp_key: *string* Component key corresponding to the station coordinates.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> a.update_from_station_coords()
        """
        # -----------------------------------------------------------------------

        for IQ_name in self.IQ_names:
            IQ = self.IQ_data[IQ_name]

            if IQ.station_obj is None:
                continue
            if comp_key is not None and IQ.comp_key != comp_key:
                continue

            iaxis = axis_index[IQ.coord_axis]
            IQ.coord = IQ.station_obj.Coordinates[iaxis]

    # ===========================================================================
    def set_IQ_name(self, station_ref, ISO, IQ_new_name):
        """
        Sets or replaces the IQ name in the given station_ref and ISO

        :param self: *object* ELS_data class object.
        :param station_ref: *string* station reference.
        :param ISO: *string* Corresponding ISO value.
        :param IQ_new_name: *string* new IQ name.

        :return: *None*

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> station_ref = "xxx"
        >>> ISO = "yyy"
        >>> IQ_new_name = "z"
        >>> a.set_IQ_name(station_ref, ISO, IQ_new_name)
        """
        ISO = int(ISO)

        if "#" in station_ref:
            (comp_key, tag, station_num) = station_ref.partition("#")
            ind_station = int(station_num) - 1

        elif "." in station_ref:
            (comp_key, tag, station_id) = station_ref.partition(".")
            for ind_IQ, IQ in enumerate(self.plot_data2[comp_key][ISO]["IQ_list"]):
                if IQ.station == station_ref:
                    ind_station = ind_IQ
                    break
        else:
            error_msg = "invalid station reference"
            print(
                "set_IQ_name: %s %s,%s -> %s"
                % (error_msg, station_ref, ISO, IQ_new_name)
            )
            return None

        # -----------------------------------------------------------------------

        if comp_key not in self.plot_data2:
            error_msg = "invalid comp_key"
            print(
                "set_IQ_name: %s %s,%s -> %s"
                % (error_msg, station_ref, ISO, IQ_new_name)
            )
            return None

        if (
            ind_station is None
            or ind_station < 0
            or ind_station >= len(self.plot_data2[comp_key][ISO]["IQ_list"])
        ):
            error_msg = "invalid station reference"
            print(
                "set_IQ_name: %s %s,%s -> %s"
                % (error_msg, station_ref, ISO, IQ_new_name)
            )
            return None

        if ISO not in self.plot_data2[comp_key]:
            error_msg = "invalid ISO"
            print(
                "set_IQ_name: %s %s,%s -> %s"
                % (error_msg, station_ref, ISO, IQ_new_name)
            )
            return None

        IQ = self.plot_data2[comp_key][ISO]["IQ_list"][ind_station]
        IQ_old_name = IQ.name

        if self.rename_IQ(IQ_old_name, IQ_new_name):
            return IQ_old_name

        return None

    # ===========================================================================
    def rename_IQ(self, IQ_old_name, IQ_new_name):
        """
        Replaces the old IQ name with the new IQ name

        :param self: *object* ELS_data class object.
        :param IQ_old_name: *string* Old IQ name.
        :param IQ_new_name: *string* New IQ name to replace.

        :return: *bool* Returns True after sucessful rename.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> IQ_old_name = "xxx"
        >>> IQ_new_name = "yyy"
        >>> a.rename_IQ(IQ_old_name, IQ_new_name)
        """
        if IQ_old_name not in self.IQ_data:
            print("rename_IQ: %s -> %s invalid IQ name" % (IQ_old_name, IQ_new_name))
            return False

        if IQ_new_name in self.IQ_data:
            print(
                "rename_IQ: %s -> %s target IQ name already exists"
                % (IQ_old_name, IQ_new_name)
            )
            return False

        IQ = self.IQ_data[IQ_old_name]

        IQ.name = IQ_new_name

        # print ("IQ renamed: %s -> %s" % (IQ_old_name,IQ_new_name))

        return True

    # ===========================================================================
    def reorganize_IQ_data(self):
        """
        Reorganize IQ data

        :param self: *object* ELS_data class object.

        :return: *dict* Returns modified IQ data.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> IQ_names_modified = a.reorganize_IQ_data()
        """
        self.set_station_ref()

        IQ_names = []
        IQ_data = {}
        AC_param = {}

        plot_data1 = {}
        plot_data2 = {}
        IQ_tree = {}

        modified_IQ_names = {}

        for IQ_name in self.IQ_names:
            IQ = self.IQ_data[IQ_name]
            IQ_names.append(IQ.name)
            IQ_data[IQ.name] = IQ
            if IQ.comp_key == "AC":
                AC_param[IQ.name] = IQ
            if IQ.name != IQ_name:
                modified_IQ_names[IQ_name] = IQ.name

            # -----------------------------------------------------------------------

            if not IQ.comp_key in plot_data1:
                plot_data1[IQ.comp_key] = {}

            if not IQ.type in plot_data1[IQ.comp_key]:
                plot_data1[IQ.comp_key][IQ.type] = {}

                plot_data1[IQ.comp_key][IQ.type]["coord_axis"] = IQ.coord_axis
                plot_data1[IQ.comp_key][IQ.type]["ISO"] = IQ.ISO
                plot_data1[IQ.comp_key][IQ.type]["IQ_type"] = IQ.type
                plot_data1[IQ.comp_key][IQ.type]["IQ_unit"] = IQ.unit
                plot_data1[IQ.comp_key][IQ.type]["IQ_list"] = []
                plot_data1[IQ.comp_key][IQ.type]["IQ_names"] = []
                plot_data1[IQ.comp_key][IQ.type]["IQ_factors"] = []
                plot_data1[IQ.comp_key][IQ.type]["IQ_stations"] = []
                plot_data1[IQ.comp_key][IQ.type]["IQ_stations_desc"] = []
                plot_data1[IQ.comp_key][IQ.type]["IQ_coords"] = []

            plot_data1[IQ.comp_key][IQ.type]["IQ_list"].append(IQ)
            plot_data1[IQ.comp_key][IQ.type]["IQ_names"].append(IQ.name)
            plot_data1[IQ.comp_key][IQ.type]["IQ_factors"].append(IQ.factor)
            plot_data1[IQ.comp_key][IQ.type]["IQ_stations"].append(IQ.station)
            plot_data1[IQ.comp_key][IQ.type]["IQ_stations_desc"].append(IQ.station_desc)
            plot_data1[IQ.comp_key][IQ.type]["IQ_coords"].append(IQ.coord)

            # -----------------------------------------------------------------------

            if not IQ.comp_key in plot_data2:
                plot_data2[IQ.comp_key] = {}

            if not IQ.ISO in plot_data2[IQ.comp_key]:
                plot_data2[IQ.comp_key][IQ.ISO] = {}

                plot_data2[IQ.comp_key][IQ.ISO]["coord_axis"] = IQ.coord_axis
                plot_data2[IQ.comp_key][IQ.ISO]["ISO"] = IQ.ISO
                plot_data2[IQ.comp_key][IQ.ISO]["IQ_type"] = IQ.type
                plot_data2[IQ.comp_key][IQ.ISO]["IQ_unit"] = IQ.unit
                plot_data2[IQ.comp_key][IQ.ISO]["IQ_list"] = []
                plot_data2[IQ.comp_key][IQ.ISO]["IQ_names"] = []
                plot_data2[IQ.comp_key][IQ.ISO]["IQ_factors"] = []
                plot_data2[IQ.comp_key][IQ.ISO]["IQ_stations"] = []
                plot_data2[IQ.comp_key][IQ.ISO]["IQ_stations_desc"] = []
                plot_data2[IQ.comp_key][IQ.ISO]["IQ_coords"] = []

            plot_data2[IQ.comp_key][IQ.ISO]["IQ_list"].append(IQ)
            plot_data2[IQ.comp_key][IQ.ISO]["IQ_names"].append(IQ.name)
            plot_data2[IQ.comp_key][IQ.ISO]["IQ_factors"].append(IQ.factor)
            plot_data2[IQ.comp_key][IQ.ISO]["IQ_stations"].append(IQ.station)
            plot_data2[IQ.comp_key][IQ.ISO]["IQ_stations_desc"].append(IQ.station_desc)
            plot_data2[IQ.comp_key][IQ.ISO]["IQ_coords"].append(IQ.coord)

            # -----------------------------------------------------------------------

            if not IQ.comp_key in IQ_tree:
                IQ_tree[IQ.comp_key] = {}

            if not IQ.station_id in IQ_tree[IQ.comp_key]:
                IQ_tree[IQ.comp_key][IQ.station_id] = {}

            IQ_tree[IQ.comp_key][IQ.station_id][IQ.ISO] = IQ.name

        # -----------------------------------------------------------------------

        self.IQ_names = IQ_names
        self.IQ_data = IQ_data
        self.AC_param = AC_param

        self.plot_data1 = plot_data1
        self.plot_data2 = plot_data2

        self.sort_plot_data()

        return modified_IQ_names

    # ===========================================================================
    def get_IQ_names(self, comp_key=None, IQ_type=None):
        """
        returns the IQ names for a given comp_key and IQ type
        if comp_key is omitted the IQ names for all components are returned
        if IQ_type is omitted the IQ_names for all IQ types are returned

        :param self: *object* ELS_data class object.
        :param comp_key: *string* Component key.
        :param IQ_type: *string* IQ type.

        :return: *dict* Returns modified IQ names.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> IQ_names = a.get_IQ_names()
        """
        # -----------------------------------------------------------------------

        if comp_key is None:
            return self.IQ_names

        if comp_key not in self.plot_data1:
            return []

        if IQ_type is None:
            IQ_names = []
            comp_plot_data = self.plot_data1[comp_key]

            for IQ_type in comp_plot_data.keys():
                for IQ_name in comp_plot_data[IQ_type]["IQ_names"]:
                    IQ_names.append(IQ_name)
            return IQ_names

        if isinstance(IQ_type, str):
            if IQ_type in self.plot_data1[comp_key]:
                comp_plot_data = self.plot_data1[comp_key]
                return comp_plot_data[IQ_type]["IQ_names"]

        if isinstance(IQ_type, int):
            if IQ_type in self.plot_data2[comp_key]:
                comp_plot_data = self.plot_data2[comp_key]
                return comp_plot_data[IQ_type]["IQ_names"]

        return []

    # ===========================================================================
    def has_IQ(self, IQ_name):
        """
        checks whether IQ_name is a valid IQ name

        :param self: *object* ELS_data class object.
        :param IQ_name: *string* IQ name.

        :return: *bool* Returns true if IQ name is valid else returns false.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> isValid = a.has_IQ("IQ_NAME")
        """
        # -----------------------------------------------------------------------

        if IQ_name in self.IQ_names:
            return True
        else:
            return False

    # ===========================================================================
    def get_IQ_def(self, IQ_name):
        """
        returns the object for a given IQ name

        :param self: *object* ELS_data class object.
        :param IQ_name: *string* IQ name.

        :return: *object* Returns IQ object.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> iq_obj = a.get_IQ_def("IQ_NAME")
        """
        # -----------------------------------------------------------------------

        if IQ_name in self.IQ_names:
            return self.IQ_data[IQ_name]

        return None

    # ===========================================================================
    def get_IQ_attribute(self, IQ_name, attr_name):
        """
        returns the attribute value for a given IQ and attribute name

        :param self: *object* ELS_data class object.
        :param IQ_name: *string* IQ name.
        :param attr_name: *string* attribute name.

        :return: *string* Returns attribute value.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> comp_key = a.get_IQ_attribute("IQ_NAME", "comp_key")
        """
        # -----------------------------------------------------------------------

        if IQ_name in self.IQ_name_set:
            IQ = self.IQ_data[IQ_name]
            return IQ.get_attribute(attr_name)
        return None

    # ===========================================================================
    def set_IQ_attribute(self, IQ_name, attr_name, value):
        """
        sets the attribute value for a given IQ and attribute name

        :param self: *object* ELS_data class object.
        :param IQ_name: *string* IQ name.
        :param attr_name: *string* attribute name.
        :param value: *string* attribute value.

        :return: *None*

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> a.set_IQ_attribute("IQ_NAME", "unit", "value")
        """
        # -----------------------------------------------------------------------

        if IQ_name in self.IQ_names:
            IQ = self.IQ_data[IQ_name]

            if attr_name in ELS_data.IQ_attr_names:
                return IQ.set_attribute(attr_name, value)
            elif attr_name in ELS_data.ELS_column_names:
                get_name = ELS_data.ELS_column_to_IQ_attr_name_mapping[attr_name]
                return IQ.set_attribute(get_name, value)
            else:
                return None

        return None

    # ===========================================================================
    def set_IQ_attributes(self, IQ_name, attr_dict):
        """
        sets the attribute values for a given IQ given in attr_dict

        :param self: *object* ELS_data class object.
        :param IQ_name: *string* IQ name.
        :param attr_dict: *dict* attribute dict.

        :return: *bool* Returns true if the operation is successful else returns false.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> IQ_attr = {
        >>>     "ISO": ISO,
        >>>      "type": IQ_type,
        >>>      "unit": IQ_unit,
        >>>      "factor": IQ_factor,
        >>> }
        >>> isSuccess = a.set_IQ_attributes("IQ_NAME", IQ_attr)
        """
        # -----------------------------------------------------------------------

        if IQ_name not in self.IQ_data:
            print("set_IQ_attributes: %s invalid IQ name" % IQ_name)
            return False

        IQ = self.IQ_data[IQ_name]

        IQ.set_attr_dict(attr_dict)

        return True

    # ===========================================================================
    def get_IQ_station(self, IQ_name):
        """
        returns the output station for a given IQ name

        :param self: *object* ELS_data class object.
        :param IQ_name: *string* IQ name.

        :return: *string* Returns IQ station.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> IQ_station = a.get_IQ_station(IQ_name)
        """
        # -----------------------------------------------------------------------

        if IQ_name in self.IQ_names:
            return self.IQ_data[IQ_name].station

        return None

    # ===========================================================================
    def set_IQ_station(self, IQ_name, station_name):
        """
        sets the output station for a given IQ name

        :param self: *object* ELS_data class object.
        :param IQ_name: *string* IQ name.
        :param station_name: *string* station name.

        :return: *None*

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> a.set_IQ_station("IQ_NAME", "station_name")
        """
        # -----------------------------------------------------------------------

        if IQ_name in self.IQ_names:
            IQ = self.IQ_data[IQ_name]

            IQ.set_attribute("station", station_name)
            IQ.station_obj = None
            IQ.station_desc = None
            IQ.coord = None

        return None

    # ===========================================================================
    def get_IQ_names_at_station(self, station_name):
        """
        get the list of IQ_names from all IQs at a given station

        :param self: *object* ELS_data class object.
        :param station_name: *string* station name.

        :return: *list* Returns IQ names list.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> IQ_Names = a.get_IQ_names_at_station("station_name")
        """
        # -----------------------------------------------------------------------

        IQ_names_at_station = []

        for IQ_name in self.IQ_names:
            IQ = self.IQ_data[IQ_name]

            if IQ.station is not None and IQ.station == station_name:
                IQ_names_at_station.append(IQ_name)

        return IQ_names_at_station

    # ===========================================================================
    def get_AC_param_names(self):
        """
        returns the list of AC_param IQ names

        :param self: *object* ELS_data class object.

        :return: *list* Returns list of AC_param IQ names.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> names = a.get_AC_param_names()
        """
        # -----------------------------------------------------------------------

        return sorted(self.AC_param.keys())

    # ===========================================================================
    def get_AC_param_data(self, IQ_name=None):
        """
        returns the data for a given AC_param IQ name (or the complete data structure)

        :param self: *object* ELS_data class object.
        :param IQ_name: *string* IQ name.

        :return: *dict* Returns AC param data.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> data = a.get_AC_param_data("IQ_NAME")
        """
        # -----------------------------------------------------------------------

        if IQ_name is None:
            return self.AC_param
        else:
            if IQ_name in self.AC_param.keys():
                return self.AC_param[IQ_name]
            else:
                return None

    # ===========================================================================
    def has_component(self, comp_key):
        """
        checks whether comp_key is a valid component key

        :param self: *object* ELS_data class object.
        :param comp_key: *string* component key.

        :return: *bool* Returns true if the component key is valid else returns false.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> isValid = a.has_component("component_key")
        """
        # -----------------------------------------------------------------------

        if comp_key in self.plot_data1:
            return True
        else:
            return False

    # ===========================================================================
    def get_plot_data(self, comp_key=None, IQ_type=None):
        """
        returns the plot data for a given comp_key and IQ type
        if IQ_type is omitted the plot data for all IQ types is returned
        if comp_key is omitted the complete plot data for all components is returned

        :param self: *object* ELS_data class object.
        :param comp_key: *string* IQ name.
        :param IQ_type: *string* IQ type.

        :return: *dict* Returns plot data.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> plot_data = a.get_plot_data("comp_key", "IQ_type")
        """
        # -----------------------------------------------------------------------

        # print ("get_plot_data: %s -> %s" % (comp_key,IQ_type))

        if comp_key is None:
            return self.plot_data1

        if comp_key not in self.plot_data1.keys():
            return None

        if IQ_type is None:
            comp_plot_data = self.plot_data1[comp_key]
            return comp_plot_data

        if isinstance(IQ_type, str):
            if IQ_type in self.plot_data1[comp_key]:
                comp_plot_data = self.plot_data1[comp_key]
                return self.plot_data1[comp_key][IQ_type]

        if isinstance(IQ_type, int):
            if IQ_type in self.plot_data2[comp_key]:
                return self.plot_data2[comp_key][IQ_type]
            elif IQ_type == 0:
                return self.plot_data2[comp_key]

        return None

    # ===========================================================================
    def get_plot_data2(self, comp_key=None, ISO=None):
        """
        returns the plot tree for a given comp_key and ISO
        if ISO is omitted the plot data for all ISOs is returned
        if comp_key is omitted the complete plot tree for all components is returned

        :param self: *object* ELS_data class object.
        :param comp_key: *string* component key.
        :param ISO: *string* ISO.

        :return: *dict* Returns plot tree.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> plot_data = a.set_IQ_attributes("comp_key", "ISO")
        """
        # -----------------------------------------------------------------------

        if comp_key is None:
            return self.plot_data2

        if comp_key in self.plot_data2.keys():
            comp_plot_data = self.plot_data2[comp_key]

            if ISO is None:
                return comp_plot_data

            if ISO in comp_plot_data.keys():
                return comp_plot_data[ISO]

        return None

    # ===========================================================================
    def get_CQ_dict(self):
        """
        returns the dict of 2D correlations

        :param self: *object* ELS_data class object.

        :return: *dict* Returns dict of 2D correlations.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> out = a.get_CQ_dict()
        """
        # -----------------------------------------------------------------------

        return self.CQ_dict

    # ===========================================================================
    def get_comp_ISO_units(self):
        """
        returns a dict with the unit string and factor for all comp keys and ISOs

        :param self: *object* ELS_data class object.

        :return: *dict* Returns dict for all component keys and ISOs.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> data = a.get_comp_ISO_units()
        """
        # -----------------------------------------------------------------------

        comp_ISO_units = {}

        for comp_key in self.plot_data2.keys():
            comp_plot_data = self.plot_data2[comp_key]
            comp_ISO_units[comp_key] = {}

            for ISO in comp_plot_data.keys():
                comp_ISO_data = comp_plot_data[ISO]

                if len(comp_ISO_data["IQ_list"]) > 0:
                    IQ = comp_ISO_data["IQ_list"][0]
                    comp_ISO_units[comp_key][ISO] = {}
                    comp_ISO_units[comp_key][ISO]["unit"] = IQ.unit
                    comp_ISO_units[comp_key][ISO]["factor"] = IQ.factor

        return comp_ISO_units

    # ===========================================================================
    def get_mirror_def_data(self):
        """
        returns the mirror definition data

        :param self: *object* ELS_data class object.

        :return: *list* Returns mirror defination data.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> data = a.get_mirror_def_data()
        """
        # -----------------------------------------------------------------------

        mirror_def_data = []

        for IQ1_name in self.IQ_names:
            IQ1_obj = self.IQ_data[IQ1_name]

            if IQ1_obj.mirror_flag:
                # print ("IQ: %s (%s) = %s" % (IQ1_name,IQ1_obj.mirror_flag,IQ1_obj.formula))

                mirr_formula = (
                    IQ1_obj.formula.strip()
                )  # remove leading + trailing blanks
                mirr_formula = "".join(mirr_formula.split())  # remove internal blanks

                if mirr_formula.count("$") != 1 or mirr_formula.count("*") != 1:
                    print(
                        "get_mirror_def_data: Invalid mirror formula: %s"
                        % IQ1_obj.formula
                    )
                    continue

                factor, sep, IQ2_name = mirr_formula.partition("*${")

                if IQ2_name.endswith("}"):
                    IQ2_name = IQ2_name[:-1]

                if not IQ2_name in self.IQ_names:
                    print("get_mirror_def_data: Invalid IQ name: %s" % IQ1_obj.formula)
                    continue

                try:
                    factor = float(factor)
                except:
                    print(
                        "get_mirror_def_data: Invalid factor value: %s"
                        % IQ1_obj.formula
                    )
                    continue

                mirror_def_data.append([IQ1_name, IQ2_name, factor])

        return mirror_def_data

    # ===========================================================================
    def write_file(self, file_name):
        """
        write the data from memory into an (csv) file

        :param self: *object* ELS_data class object.
        :param self: *string* file name.

        :return: *int* Returns 1 on success and None on failure.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> isSuccess = a.write_file("file_name")
        """
        # -----------------------------------------------------------------------
        # check file name
        if not file_name:
            print("els_data.write_file: Error - Empty file name")
            return None

        # -----------------------------------------------------------------------
        # open file
        file_obj = File_rw(file_name, "w")

        # -----------------------------------------------------------------------
        # write header line
        headline = ",".join(ELS_data.ELS_column_names)
        file_obj.write_line(headline)

        # write data lines
        for IQ_name in sorted(self.IQ_names):
            csv_line = self.get_csv_line(IQ_name)
            file_obj.write_line(csv_line)

        # -----------------------------------------------------------------------
        # close the file
        file_obj.close()
        file_obj = None

        return 1

    # ===========================================================================
    def get_csv_data(self):
        """
        returns the complete data as list of csv strings

        :param self: *object* ELS_data class object.

        :return: *list* Returns list of csv strings.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> data = a.get_csv_data()
        """
        csv_data = []
        for IQ_name in sorted(self.IQ_names):
            csv_line = self.get_csv_line(IQ_name)
            csv_data.append(csv_line)

        return csv_data

    # ===========================================================================
    def get_csv_line(self, IQ_name):
        """
        return a csv line for an IQ

        :param self: *object* ELS_data class object.
        :param self: *string* IQ name.

        :return: *string* Returns CSV line.

        :examples:
        >>> from fp_dataio.Domain.els_data import ELS_data
        >>> a = ELS_data()
        >>> line = a.get_csv_line("IQ_NAME")
        """
        if IQ_name not in self.IQ_data:
            return IQ_name

        IQ = self.IQ_data[IQ_name]

        fields = []
        for column_name in ELS_data.ELS_column_names:
            attr_name = ELS_data.ELS_column_to_IQ_attr_name_mapping[column_name]
            if attr_name == "station":
                attr_name = "station_id"
            attr_value = IQ.get_attribute(attr_name)
            if attr_value is None:
                attr_value = ""
            fields.append(str(attr_value))

        if IQ.comp_key == "AC":
            fields[ELS_data.ind_col_station] = "%04d" % IQ.ISO
            fields[ELS_data.ind_col_ISO] = "01"

        csv_line = ",".join(fields)

        return csv_line


################################################################################
class IQ_def(object):
    """
    IQ definition object methods
    """

    # ===========================================================================
    def __init__(self, def_dict):
        """
        Constructor
        """
        self.name = None
        self.comp_key = None
        self.comp_name = ""
        self.station = None
        self.station_id = None
        self.station_type = None
        self.station_desc = None
        self.station_index = None
        self.station_obj = None
        self.CID = None
        self.rotation_flag = None
        self.DOF = None
        self.load_type = None
        self.qualifier = ""
        self.SISO = None
        self.ISO = None
        self.type = None
        self.unit = ""
        self.factor = None
        self.skill_mark = ""
        self.mirror_flag = None
        self.sel_flag = None
        self.DB_flag = None
        self.keyword = ""
        self.formula = ""
        self.comment = ""
        self.index = None
        self.coord_axis = ""
        self.coord = None
        self.plf2d_name = None

        self.set_attr_dict(def_dict)

        # print ("New IQ: %s (%s, %s)" % (self.name,self.station,self.station_id))

    # ===========================================================================
    def get_def_dict(self):
        """ """
        def_dict = {}

        for attr_name in ELS_data.IQ_attr_names:
            def_dict[attr_name] = getattr(self, attr_name)

        return def_dict

    # ===========================================================================
    def set_attr_dict(self, attr_dict):
        for attr_name in attr_dict:
            if attr_name in ELS_data.IQ_attr_names_set:
                setattr(self, attr_name, attr_dict[attr_name])
            elif attr_name in ELS_data.ELS_column_names:
                set_name = ELS_data.ELS_column_to_IQ_attr_name_mapping[attr_name]
                setattr(self, set_name, attr_dict[attr_name])

        if self.SISO is not None:
            try:
                self.SISO = int(self.SISO)
            except:
                self.SISO = 0

        if self.ISO is not None:
            try:
                self.ISO = int(self.ISO)
            except:
                self.ISO = 0

        if self.CID is not None:
            try:
                self.CID = int(self.CID)
            except:
                self.CID = 0

        if self.DOF is not None:
            try:
                self.DOF = int(self.DOF)
            except:
                self.DOF = 0

        if self.factor is not None:
            try:
                self.factor = float(self.factor)
            except:
                self.factor = 1.0

        if self.mirror_flag is not None:
            try:
                self.mirror_flag = int(self.mirror_flag)
            except:
                self.mirror_flag = 0

        if self.station is not None:
            self.station = self.station.lstrip()  # remove leading whitespaces
            if self.station.startswith(self.comp_key + "."):
                self.station_id = self.station.split(".")[1]
                while len(self.station_id) > 1 and self.station_id.startswith("0"):
                    self.station_id = self.station_id[1:]  # remove leading zeros
                self.station = self.comp_key + "." + self.station_id
            else:
                self.station_id = self.station
                while len(self.station_id) > 1 and self.station_id.startswith("0"):
                    self.station_id = self.station_id[1:]  # remove leading zeros
                self.station = self.comp_key + "." + self.station_id

    # ===========================================================================
    def get_attribute(self, attr_name):
        """ """
        if attr_name in ELS_data.IQ_attr_names:
            return getattr(self, attr_name)
        elif attr_name in ELS_data.ELS_column_names:
            attr_name = ELS_data.ELS_column_to_IQ_attr_name_mapping[attr_name]
            return getattr(self, attr_name)
        else:
            return None

    # ===========================================================================
    def set_attribute(self, attr_name, value):
        """ """
        self.set_attr_dict({attr_name: value})


################################################################################
