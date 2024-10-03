This module contains child classes of the Data class which are used to read specific file types.

The Data class is a generic data object which is used to store data from different file types.


# Table of Contents

- [`ECLab_File`](#`eclab_file`)
  - [`__init__`](#`__init__`)
  - [`set_commonly_accessed_attributes`](#`set_commonly_accessed_attributes`)
  - [`extract_data`](#`extract_data`)
  - [`cycle`](#`cycle`)
  - [`cycles`](#`cycles`)

# `ECLab_File`

**Description:**

This class is used to read data from an ECLab txt file.



**Parent Class:**

Data


## `__init__`

**Arguments:**

- *file_name: str (optional)

The path of the file to be read



**Methodology:**

- self.data_type is set to 'ECLab_File'.

- Data is extracted from the file, stored in self.data, and the data_names are stored in self.data_names.

- The start and end times are set.

- The commonly accessed attributes are set.


## `set_commonly_accessed_attributes`

**Description:**

INTERNAL FUNCTION CALLED DURING INITIALIZATION.

For an ECLab file, the commonly accessed attributes are time/s, Ewe/V, I/mA and cycle number.

The data for these is stored in the attributes t, E, I and c respectively.


## `extract_data`

**Description:**

INTERNAL FUNCTION CALLED DURING INITIALIZATION.

This function handles reading the data from the text file, handling the time data, and storing everything in the self.data dictionary.



**Arguments:**

- file_name: str

The path of the ECLab txt file to be read.



**Methodology:**

- The data is extracted from the file

- The data_names are stored in self.data_names

- Time is converted to elapsed time and the start and end times are set.

- All data stored as numpy arrays in self.data


## `cycle`

**Arguments:**

- c: int or float

The cycle number to be extracted.



**Returns:**

- ECLab_File object

The ECLab_File object containing only the data from the specified cycle.


## `cycles`

**Arguments:**

- *cycles: int or float

The cycle numbers to be extracted.



**Returns:**

- ECLab_File object

The ECLab_File object containing only the data from the specified cycles.


