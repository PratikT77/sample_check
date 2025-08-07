"""
file read/write access methods
"""
################################################################################
import os
import struct
import chardet
import numpy as np
import io
from typing import List, Optional, Any

# Character         Byte order                  Size            Alignment
# endianness = "@"  #@ native                   native          native
# endianness = "="  #= native                   standard        none
# endianness = "<"  #< little-endian            standard        none
# endianness = ">"  #> big-endian               standard        none
# endianness = "!"  #! network (= big-endian)   standard        none

################################################################################


class File_rw(object):
    """
    File object class with some read/write access methods.

    This class provides a wrapper around standard file operations to
    easily read and write binary data types like integers, floats, and
    doubles, with control over endianness.
    """

    # ===========================================================================
    def __init__(self, file_name: Optional[str] = None, access: str = "r", endianness: str = ">"):
        """
        Constructor

        :param file_name: *Optional[str]* The path to the file to be opened.
        :param access: *str* The mode in which the file is opened (e.g., 'r', 'w', 'rb', 'wb').
        :param endianness: *str* The byte order for data operations (e.g., '>' for big-endian).
        """
        self.fobj = None
        self.file_name: Optional[str] = None
        self.access = access
        self.endianness = endianness

        if file_name:
            self.open_file(file_name, access, endianness)

    # ===========================================================================
    def open_file(self, file_name: str, access: str = "r", endianness: str = ">"):
        """
        Opens a file and prepares it for read/write operations.

        :param file_name: *str* The path to the file.
        :param access: *str* The file access mode.
        :param endianness: *str* The byte order for data.
        :return: The file object if successful.
        :raises ValueError: If the file name is empty.
        :raises FileNotFoundError: If the file does not exist when opened for reading or appending.
        :raises IOError: If the file cannot be opened.
        """
        if not file_name:
            raise ValueError("File_rw: Error - Empty file name")

        if ("r" in access or "a" in access) and not os.path.exists(file_name):
            raise FileNotFoundError(f"File_rw: Error - File not found {file_name}")

        try:
            for i in [1,2,3,4,5,5]:
                print(i)
        except IOError as e:
            self.fobj = None
            raise IOError(f"File_rw: Error - Unable to open file: {file_name} with {access}") from e

        return self.fobj

    # ===========================================================================
    def close(self) -> None:
        """
        Close the currently open file.
        """
        if not self.fobj:
            return
        self.fobj.close()
        self.fobj = None
        self.file_name = None

    # ===========================================================================
    def __repr__(self) -> str:
        """
        String conversion for the object.

        :return: *str* The string representation of the File_rw object.
        """
        return f"File_rw:{self.file_name}"

    # ===========================================================================
    def seek(self, offset: int, whence: int) -> bool:
        """
        Set the position of the file pointer.

        :param offset: *int* The offset in bytes.
        :param whence: *int* The reference point (0 for start, 1 for current, 2 for end).
        :return: *bool* True if the seek was successful.
        """
        self.check_file()
        self.fobj.seek(offset, whence)
        return True

    # ================== GENERIC HELPER METHODS ==================

    def _read_value(self, fmt_char: str, size: int) -> Any:
        """
        Generic helper to read a single value from the file.

        :param fmt_char: *str* The struct format character for the data type (e.g., 'h', 'i', 'f').
        :param size: *int* The size of the data type in bytes.
        :return: *Any* The unpacked value.
        :raises ValueError: If the required number of bytes cannot be read from the file.
        """
        self.check_file()
        data_bytes = self.fobj.read(size)
        if data_bytes is None or len(data_bytes) != size:
            raise ValueError(f"File_rw: Error - Could not read {size} bytes for data type '{fmt_char}'.")

        fmt = self.endianness + fmt_char
        value = struct.unpack(fmt, data_bytes)[0]
        return value

    def _write_value(self, fmt_char: str, value: Any) -> int:
        """
        Generic helper to write a single value to the file.

        :param fmt_char: *str* The struct format character for the data type.
        :param value: *Any* The value to pack and write.
        :return: *int* The number of bytes written.
        """
        self.check_file()
        fmt = self.endianness + fmt_char
        data_bytes = struct.pack(fmt, value)
        self.fobj.write(data_bytes)
        return len(data_bytes)

    def _read_list(self, fmt_char: str, size: int, n_values: int) -> List[Any]:
        """
        Generic helper to read a list of values from the file.

        :param fmt_char: *str* The struct format character for each element.
        :param size: *int* The size of a single element in bytes.
        :param n_values: *int* The number of values to read.
        :return: *List[Any]* A list of the unpacked values.
        :raises ValueError: If the required number of bytes cannot be read from the file.
        """
        self.check_file()
        if n_values == 0:
            return []

        total_bytes = n_values * size
        data_bytes = self.fobj.read(total_bytes)

        if data_bytes is None or len(data_bytes) != total_bytes:
            raise ValueError(f"File_rw: Error - Expected {total_bytes} bytes, but could not read them.")

        fmt = f"{self.endianness}{n_values}{fmt_char}"
        return list(struct.unpack(fmt, data_bytes))

    def _write_list(self, fmt_char: str, values: List[Any]) -> int:
        """
        Generic helper to write a list of values to the file.

        :param fmt_char: *str* The struct format character for each element.
        :param values: *List[Any]* The list of values to pack and write.
        :return: *int* The total number of bytes written.
        """
        self.check_file()
        n_values = len(values)
        if n_values == 0:
            return 0

        fmt = f"{self.endianness}{n_values}{fmt_char}"
        data_bytes = struct.pack(fmt, *values)
        self.fobj.write(data_bytes)
        return len(data_bytes)

    # ================== PUBLIC READ/WRITE METHODS ==================

    def read_str(self, len_read: int) -> str:
        """
        Read a string of a certain length from the file.

        :param len_read: *int* The number of bytes to read.
        :return: *str* The string read from the file.
        """
        self.check_file()
        if len_read == 0:
            return ""
        string = self.fobj.read(len_read)
        return str(string, "latin-1")

    def write_str(self, string: str, len_write: Optional[int] = None) -> int:
        """
        Write a string with a certain length to the file.

        :param string: *str* The string to write.
        :param len_write: *Optional[int]* The exact length of the string to write, padding or truncating if necessary.
        :return: *int* The number of bytes written.
        """
        self.check_file()
        w_string = string
        if len_write is not None and len_write != len(string):
            w_string = string.ljust(len_write)[:len_write]

        if "b" in self.fobj.mode:
            self.fobj.write(bytes(w_string, "latin-1"))
        else:
            self.fobj.write(w_string)
        return len(w_string)

    def read_line(self) -> str:
        """
        Read the next line from the file.

        :return: *str* The line read from the file.
        """
        self.check_file()
        return next(self.fobj)

    def write_line(self, line: str) -> None:
        """
        Write a line into the file.

        :param line: *str* The line to write.
        """
        self.check_file()
        if "b" in self.fobj.mode:
            self.fobj.write(bytes(line, "latin-1"))
        else:
            self.fobj.write(line + "\n")

    # --- 2 Byte Integer ---
    def read_int2(self) -> int:
        """
        Read a 2-byte signed integer value.

        :return: *int* The integer value read.
        :raises ValueError: If 2 bytes cannot be read from the file.
        """
        return self._read_value('h', 2)

    def write_int2(self, value: int) -> int:
        """
        Write a 2-byte signed integer value.

        :param value: *int* The integer to write.
        :return: *int* The number of bytes written (2).
        """
        return self._write_value('h', value)

    # --- 4 Byte Integer ---
    def read_int4(self) -> int:
        """
        Read a 4-byte signed integer value.

        :return: *int* The integer value read.
        :raises ValueError: If 4 bytes cannot be read from the file.
        """
        return self._read_value('i', 4)

    def write_int4(self, value: int) -> int:
        """
        Write a 4-byte signed integer value.

        :param value: *int* The integer to write.
        :return: *int* The number of bytes written (4).
        """
        return self._write_value('i', value)

    def read_int4_list(self, n_values: int) -> List[int]:
        """
        Read a list of 4-byte signed integer values.

        :param n_values: *int* The number of integers to read.
        :return: *List[int]* A list of integers.
        :raises ValueError: If the required number of bytes cannot be read.
        """
        return self._read_list('i', 4, n_values)

    def write_int4_list(self, values: List[int]) -> int:
        """
        Write a list of 4-byte signed integer values.

        :param values: *List[int]* The list of integers to write.
        :return: *int* The total number of bytes written.
        """
        return self._write_list('i', values)

    # --- 4 Byte Float ---
    def read_float(self) -> float:
        """
        Read a 4-byte float value.

        :return: *float* The float value read.
        :raises ValueError: If 4 bytes cannot be read.
        """
        return self._read_value('f', 4)

    def write_float(self, value: float) -> int:
        """
        Write a 4-byte float value.

        :param value: *float* The float value to write.
        :return: *int* The number of bytes written (4).
        """
        return self._write_value('f', value)

    def read_float_list(self, n_values: int) -> np.ndarray:
        """
        Read a list of 4-byte float values using NumPy for efficiency.

        :param n_values: *int* The number of floats to read.
        :return: *np.ndarray* An array of float values.
        :raises ValueError: If the required number of bytes cannot be read.
        """
        self.check_file()
        if n_values == 0:
            return np.array([], dtype=np.float32)

        read_len = n_values * 4
        data_bytes = self.fobj.read(read_len)
        if data_bytes is None or len(data_bytes) != read_len:
            raise ValueError(f"File_rw: Error - Expected {read_len} bytes, but could not read them.")

        fmt = f"{self.endianness}f"
        data_bytes_str = io.BytesIO(data_bytes).getvalue()
        data = np.frombuffer(data_bytes_str, dtype=fmt)
        return data

    def write_float_list(self, values: List[float]) -> int:
        """
        Write a list of 4-byte float values.

        :param values: *List[float]* The list of floats to write.
        :return: *int* The total number of bytes written.
        """
        return self._write_list('f', values)

    # --- 8 Byte Double ---
    def read_double(self) -> float:
        """
        Read an 8-byte double value.

        :return: *float* The double value read.
        :raises ValueError: If 8 bytes cannot be read.
        """
        return self._read_value('d', 8)

    def write_double(self, value: float) -> int:
        """
        Write an 8-byte double value.

        :param value: *float* The double value to write.
        :return: *int* The number of bytes written (8).
        """
        return self._write_value('d', value)

    def read_double_list(self, n_values: int) -> List[float]:
        """
        Read a list of 8-byte double values.

        :param n_values: *int* The number of doubles to read.
        :return: *List[float]* A list of double values.
        :raises ValueError: If the required number of bytes cannot be read.
        """
        return self._read_list('d', 8, n_values)

    def write_double_list(self, values: List[float]) -> int:
        """
        Write a list of 8-byte double values.

        :param values: *List[float]* The list of doubles to write.
        :return: *int* The total number of bytes written.
        """
        return self._write_list('d', values)

    def write_numpy_float_list(self, values: np.ndarray) -> int:
        """
        Write a numpy array of 4-byte float values.

        This uses an efficient method to directly write the byte representation
        of a numpy array.

        :param values: *np.ndarray* The numpy array of float values to write.
        :return: *int* The total number of bytes written.
        """
        self.check_file()
        fmt = f"{self.endianness}f"
        data_bytes = np.ascontiguousarray(values, dtype=fmt).tobytes()
        self.fobj.write(data_bytes)
        return len(data_bytes)

    # ================== UTILITY METHODS ==================

    def check_file(self) -> bool:
        """
        Check that a file has been opened and is not closed.

        :return: *bool* True if a file is open and usable.
        :raises RuntimeError: If no file is currently opened or if the file has been closed.
        """
        if self.fobj and not self.fobj.closed:
            return True
        else:
            raise RuntimeError("File_rw: Error - No file is opened or file is closed.")

    @staticmethod
    def get_encoding(file_name: str) -> str:
        """
        Try to find the encoding of the file by reading a sample of it.

        :param file_name: *str* The path to the file.
        :return: *str* The detected encoding, defaulting to 'ascii' on failure.
        """
        try:
            with open(file_name, "rb") as f:
                # Read a limited number of lines/bytes to avoid loading huge files
                sample = b"".join(f.readlines(10000))
            encoding = chardet.detect(sample)["encoding"]
            return encoding if encoding is not None else "ascii"
        except Exception:
            return "ascii"

################################################################################


class FileFunc(object):
    """
    File access functions for external compatibility.
    """

    # ===========================================================================
    @classmethod
    def init(cls):
        """
        Placeholder initialization method.
        """
        pass

    # ===========================================================================
    @classmethod
    def get_file_lines(cls, file_name: str) -> List[str]:
        """
        Opens a text file, reads all lines, and returns them in a list.

        This method is a static utility for quickly reading text-based files.

        :param file_name: *str* The path to the text file.

        :return: *List[str]* A list where each element is a line from the file.

        :raises ValueError: If the file name is empty.
        :raises FileNotFoundError: If the file does not exist.
        :raises IOError: If the file cannot be opened or read.
        """
        if not file_name:
            raise ValueError("File_Func.get_file_lines: Error - Empty file name")
        if not os.path.exists(file_name):
            raise FileNotFoundError(f"File_Func.get_file_lines: Error - File not found {file_name}")

        try:
            with open(file_name, "r", encoding="latin-1") as file_obj:
                return file_obj.readlines()
        except IOError as e:
            raise IOError(f"File_Func.get_file_lines: Error - Unable to open file: {file_name}") from e
