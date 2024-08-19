# This library is used for extracting data from various filetypes.
# There is a generic Data object which is used to store the data.

import numpy as np
import datetime

class Data:
    def __init__(self):
        self.data = {}
        self.data_names = []
        self.time_format = ''
        self.start_time, self.end_time = 0, 0
        self.data_type = 'Data'

    def convert_datetime_to_elapsed_time(self, time):
        # This function takes an absolute time and converts it to elapsed time.
        # Converted to datetime object using self.time_format.
        # If self.start_time not already set, then sets provided time to start_time.
        datetime_object = datetime.datetime.strptime(time, self.time_format)
        if self.start_time == 0: self.start_time = datetime_object
        return (datetime_object - self.start_time).total_seconds()
    
    def convert_elapsed_time_to_datetime(self, time):
        # This function takes an elapsed time in seconds and, using self.start_time,
        # converts this to an absolute time.
        # If self.start_time is not set, then the elapsed time is returned.
        if self.start_time == 0: return time
        return self.start_time + datetime.timedelta(seconds=time)
    
    def set_commonly_accessed_attributes(self, data_names, attribute_aliases):
        # This function takes a list of data_names and a list of attribute_aliases.
        # If data_name is a key in self.data then the data_list is set as an attribute
        # of the Data object using the provided alias.
        for data_name, attribute_alias in zip(data_names, attribute_aliases):
            if data_name in self.data_names: setattr(self, attribute_alias, self.data[data_name])

class ECLab_File(Data):
    def __init__(self, *file_name):
        Data.__init__(self)
        self.time_format = "%m/%d/%Y %H:%M:%S.%f"
        self.data_type = 'ECLab_File'

        if file_name: self.extract_data(file_name[0])
        self.set_commonly_accessed_attributes(
            ['time/s',  'Ewe/V',    'I/mA', 'cycle number'],
            ['t',       'E',        'I',    'cycle']
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
                    if ':' in value: self.data[data_name].append(self.convert_datetime_to_elapsed_time(value))
                    else: self.data[data_name].append(float(value))
            for data_name in self.data_names: self.data[data_name] = np.array(self.data[data_name])

        # Finally set the end_time, assuming that 'time/s' has been recorded.
        if 'time/s' in self.data_names: self.end_time = self.convert_elapsed_time_to_datetime(self.data['time/s'][-1])



