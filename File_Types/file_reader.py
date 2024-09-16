'''
This module contains child classes of the Data class which are used to read specific file types.
The Data class is a generic data object which is used to store data from different file types.
'''

import numpy as np
import datetime
from ..Data import Data

class ECLab_File(Data):
    '''
    Description:
    This class is used to read data from an ECLab txt file.

    Parent Class:
    Data
    '''
    def __init__(self, *file_name):
        '''
        Arguments:
        - *file_name: str (optional)
            The path of the file to be read

        Methodology:
        - self.data_type is set to 'ECLab_File'.
        - Data is extracted from the file, stored in self.data, and the data_names are stored in self.data_names.
        - The start and end times are set.
        - The commonly accessed attributes are set.
        '''
        Data.__init__(self)
        self.time_format = "%m/%d/%Y %H:%M:%S.%f"
        self.data_type = 'ECLab_File'
        self.t_data_name = 'time/s'

        if file_name: self.extract_data(file_name[0])
        self.set_commonly_accessed_attributes()

    def set_commonly_accessed_attributes(self):
        '''
        Description:
        INTERNAL FUNCTION CALLED DURING INITIALIZATION.
        For an ECLab file, the commonly accessed attributes are time/s, Ewe/V, I/mA and cycle number.
        The data for these is stored in the attributes t, E, I and c respectively.
        '''
        self.set_attributes(
            ['time/s',  'Ewe/V',    'I/mA', 'cycle number'],
            ['t',       'E',        'I',    'c']
        )

    def extract_data(self, file_name):
        '''
        Description:
        INTERNAL FUNCTION CALLED DURING INITIALIZATION.
        This function handles reading the data from the text file, handling the time data, and storing \
        everything in the self.data dictionary.
        
        Arguments:
        - file_name: str
            The path of the ECLab txt file to be read.

        Methodology:
        - The data is extracted from the file
        - The data_names are stored in self.data_names
        - Time is converted to elapsed time and the start and end times are set.
        - All data stored as numpy arrays in self.data
        '''
        # The first line contains some mus and therefore is encoded with latin1
        # instead of the usual UTF-8
        with open(file_name, encoding='latin1') as file:
            # First read the data_names form the first line of the txt file.
            # The line ends in a newline character, so last element not counted as data_name
            # ECLab for some reason puts <> around the variable it thinks you want to measure so 
            # this is removed.
            # For every data_name, an empty list is created in the data dictionary.
            self.data_names = file.readline().split('\t')[:-1]
            self.data_names = [x.replace('µ', 'u') for x in self.data_names]
            self.data_names = [x.replace('<', '').replace('>', '') for x in self.data_names]
            for name in self.data_names: self.data[name] = []
            
            # The remaining lines are iterated through, split and appended to the correct data list.
            # If the value contians a ':' then this implies it is a date.
            # If absolute time is saved, then this is converted in to elapsed time and the start and end
            # absolute times are saved.
            # All lists are converted to numpy arrays.
            for line in file.readlines():
                values  = line.split('\t')
                for value, data_name in zip(values, self.data_names):
                    if ':' in value: self.data[data_name].append(self.convert_absolute_time_to_elapsed_time(value))
                    else: self.data[data_name].append(float(value))
            for data_name in self.data_names: self.data[data_name] = np.array(self.data[data_name])

        # Finally set the end_time, assuming that 'time/s' has been recorded.
        if 'time/s' in self.data_names: self.end_time = self.convert_elapsed_time_to_datetime(self.data['time/s'][-1])

    
    def cycle(self, c):
        '''
        Arguments:
        - c: int or float
            The cycle number to be extracted.

        Returns:
        - ECLab_File object
            The ECLab_File object containing only the data from the specified cycle.
        '''
        c = float(c)
        return self.in_data_range('c', c, c)


    def cycles(self, *cycles):
        ''' 
        Arguments:
        - *cycles: int or float
            The cycle numbers to be extracted.

        Returns:
        - ECLab_File object
            The ECLab_File object containing only the data from the specified cycles.
        '''
        cycles_list = list(cycles)
        if not cycles_list:
            raise ValueError(
                'No cycles provided. Please provide at least one cycle number.'
            )
        # If cycles are provided then the data is extracted for each cycle and combined.
        cycles_file = ECLab_File()
        cycles_file.data_names = self.data_names
        for data_name in self.data_names: cycles_file.data[data_name] = np.array([])
        for c in cycles_list:
            cycles_file += self.cycle(c)
        
        # Set the common attributes of the new object.
        cycles_file.set_commonly_accessed_attributes()
        return cycles_file
    

class Aranet_File(Data):
    '''
    Description:
    This class is used to read data from an Aranet csv file.

    Parent Class:
    Data
    '''
    def __init__(self, *file_name):
        '''
        Arguments:
        - *file_name: str (optional)
            The path of the file to be read

        Methodology:
        - self.data_type is set to 'Aranet_File'.
        - Data is extracted from the file, stored in self.data, and the data_names are stored in self.data_names.
        - The start and end times are set.
        - The commonly accessed attributes are set.
        '''
        Data.__init__(self)
        self.time_format = "%d/%m/%Y %H:%M:%S"
        self.data_type = 'Aranet_File'
        self.t_data_name = 'Time(dd/mm/yyyy)'

        if file_name: self.extract_data(file_name[0])
        self.set_commonly_accessed_attributes()
        print(self.data_names)

    def set_commonly_accessed_attributes(self):
        '''
        Description:
        INTERNAL FUNCTION CALLED DURING INITIALIZATION.
        For an ECLab file, the commonly accessed attributes are time/s, Ewe/V, I/mA and cycle number.
        The data for these is stored in the attributes t, E, I and c respectively.
        '''
        self.set_attributes(
            ['Time(dd/mm/yyyy)',  'Carbon dioxide(ppm)',    'Temperature(Â°C)', 'Relative humidity(%)', "Atmospheric pressure(hPa)"],
            ['t',       'ppm',        'T',    'RH',       "p"]
        )


    def extract_data(self, file_name):
        '''
        Description:
        INTERNAL FUNCTION CALLED DURING INITIALIZATION.
        This function handles reading the data from the text file, handling the time data, and storing \
        everything in the self.data dictionary.
        
        Arguments:
        - file_name: str
            The path of the Aranet csv file to be read.

        Methodology:
        - The data is extracted from the file
        - The data_names are stored in self.data_names
        - Time is converted to elapsed time and the start and end times are set.
        - All data stored as numpy arrays in self.data
        '''
        # The first line contains some mus and therefore is encoded with latin1
        # instead of the usual UTF-8
        with open(file_name, encoding='latin1') as file:
            # First read the data_names form the first line of the csv file.
            # The line ends in a newline character, so last element not counted as data_name
            # ECLab for some reason puts <> around the variable it thinks you want to measure so 
            # this is removed.
            # For every data_name, an empty list is created in the data dictionary.
            self.data_names = file.readline().split(',')[:-1]

            for name in self.data_names: self.data[name] = []
            
            # The remaining lines are iterated through, split and appended to the correct data list.
            # If the value contians a ':' then this implies it is a date.
            # If absolute time is saved, then this is converted in to elapsed time and the start and end
            # absolute times are saved.
            # All lists are converted to numpy arrays.
            for line in file.readlines():
                values  = line.split(',')
                for value, data_name in zip(values, self.data_names):
                    value=value.replace('"',"")
                    if ':' in value:
                        self.data[data_name].append(self.convert_absolute_time_to_elapsed_time(value))
                    else:
                        if value == "": value = np.nan
                        self.data[data_name].append(float(value))
            for data_name in self.data_names: self.data[data_name] = np.array(self.data[data_name])

        # Finally set the end_time, assuming that 'time/s' has been recorded.
        if 'Time(dd/mm/yyyy)' in self.data_names: self.end_time = self.convert_elapsed_time_to_datetime(self.data['Time(dd/mm/yyyy)'][-1])