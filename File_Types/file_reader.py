# This library is used for extracting data from various filetypes.
# There is a generic Data object which is used to store the data.

import numpy as np
import datetime
from ..Data import Data

class ECLab_File(Data):
    def __init__(self, *file_name):
        Data.__init__(self)
        self.time_format = "%m/%d/%Y %H:%M:%S.%f"
        self.data_type = 'ECLab_File'
        self.t_data_name = 'time/s'

        if file_name: self.extract_data(file_name[0])
        self.set_commonly_accessed_attributes()

    def set_commonly_accessed_attributes(self):
        self.set_attributes(
            ['time/s',  'Ewe/V',    'I/mA', 'cycle number'],
            ['t',       'E',        'I',    'c']
        )

    def extract_data(self, file_name):
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
        # This function returns a new ECLab_File object containing only the data from the specified cycle.
        c = float(c)
        return self.in_data_range('c', c, c)


    def cycles(self, *cycles):
        # This function returns a new ECLab_File object containing only the data from the specified cycles.
        # If no cycles are specified then an error is raised
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
        