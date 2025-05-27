'''
This module contains child classes of the Data class which are used to read specific file types.
The Data class is a generic data object which is used to store data from different file types.
'''

import numpy as np
import datetime
from ..Data import Data

from typing import List, Callable

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
        - Data is extracted from the file, stored in self.data, and the
            data_names are stored in self.data_names.
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
        For an ECLab file, the commonly accessed attributes are time/s, Ewe/V,
        I/mA and cycle number.
        The data for these is stored in the attributes t, E, I and c respectively.
        '''
        self.set_attributes(
            ['time/s',  'Ewe/V',    'I/mA', 'cycle number', 'Pressure/bar (on Analog In1)'],
            ['t',       'E',        'I',    'c',            'P']
        )

    def extract_data(self, file_path: str):
        '''
        Internally called function used to extract the data from either a .txt
        or .csv formatted file.

        :param file_path: The path to the ecported data file
        '''
        if    file_path.endswith('.txt'): self.extract_from_txt(file_path)
        elif  file_path.endswith('.csv'): self.extract_from_csv(file_path)
        else: raise Exception("File must be .txt or .csv")

    def extract_from_txt(self, file_path: str):
        '''
        Internally called function used to extract data from a .csv formatted 
        ECLab data file. 

        :param file_path: The path to the .txt formatted ECLab data file
        '''
        # The first line contains some mus and therefore is encoded with latin1
        # instead of the usual UTF-8
        with open(file_path, encoding='latin1') as file:
            # First read the data_names form the first line of the txt file.
            # The line ends in a newline character, so last element not counted
            # as data_name
            data_names = file.readline().split('\t')[:-1]
            self.initialise_data_dict(data_names)

            # Time can either be reported as elapsed time or in absolute date
            # format. Here we determine from the first line the time format
            # and choose the correct extraction method accordingly.
            parser = self.parse_elapsed_time_format(delimeter='\t')
            time_data_found = 'time/s' in data_names
            if time_data_found:
                time_index = data_names.index('time/s')
                line = file.readline()
                if ':' in line.split('\t')[time_index]:
                    parser = self.parse_date_time_format(time_index,
                                                         delimeter='\t')
                self.record_data(line, parser)
            
            # Using the correct parser, read in all of the data and save it.
            for line in file:
                self.record_data(line, parser)
                
            # Convert in to numpy arrays
            for data_name in self.data_names:
                self.data[data_name] = np.array(self.data[data_name])

        # Finally set the end_time, assuming that 'time/s' has been recorded.
        if time_data_found:
            end_time = self.data['time/s'][-1]
            self.end_time = self.convert_elapsed_time_to_datetime(end_time)

    def extract_from_csv(self, file_path: str):
        '''
        Internally called function used to extract data from a .txt formatted 
        ECLab data file. 

        :param file_path: The path to the .csv formatted ECLab data file
        '''
        # The first line contains some mus and therefore is encoded with latin1
        # instead of the usual UTF-8
        with open(file_path, encoding='latin1') as file:
            # For csv files the first line is formatted
            # "Technique started on : ";03/21/2025 04:33:06.786
            # Calling convert_absolute_time_to_alapsed_time set this as the 
            # start time.
            start_time = file.readline().split(';')[-1]
            # Pad to make sure correct number of decimal points
            date_part, ms_part = start_time.split('.')
            start_time = f"{date_part}.{ms_part.strip().ljust(6, '0')}"
            self.convert_absolute_time_to_elapsed_time(start_time)

            # The data names are on the next line separated by semicolons
            data_names = file.readline().split(';')[:-1]
            self.initialise_data_dict(data_names)

            # Time can either be reported as elapsed time or in absolute date
            # format. Here we determine from the first line the time format
            # and choose the correct extraction method accordingly.
            parser = self.parse_elapsed_time_format(delimeter=';')
            time_data_found = 'time/s' in data_names
            if time_data_found:
                time_index = data_names.index('time/s')
                line = file.readline()
                if ':' in line.split('\t')[time_index]:
                    parser = self.parse_date_time_format(time_index,
                                                         delimeter=';')
                self.record_data(line, parser)
            
            # Using the correct parser, read in all of the data and save it.
            for line in file:
                self.record_data(line, parser)
                
            # Convert in to numpy arrays
            for data_name in self.data_names:
                self.data[data_name] = np.array(self.data[data_name])

        # Finally set the end_time, assuming that 'time/s' has been recorded.
        if time_data_found:
            # Ensure the time starts from 0
            self.data['time/s'] = self.data['time/s'] - self.data['time/s'][0]
            end_time = self.data['time/s'][-1]
            self.end_time = self.convert_elapsed_time_to_datetime(end_time)

    def initialise_data_dict(self, data_names: List[str]):
        '''
        Internal function called by extracting data methods which reformats 
        the data_names and creates the data dictionary.

        :param data_names: List of the names of the data being read in.
        '''
        data_names = [x.replace('µ', 'u') for x in data_names]
        data_names = [x.replace('<', '')  for x in data_names]
        data_names = [x.replace('>', '')  for x in data_names]
        data_names = [x.replace('"', '')  for x in data_names]
        # Create empty list in self.data for each data name
        for name in data_names: self.data[name] = []
        self.data_names = data_names

    def parse_elapsed_time_format(self, delimeter=''):
        '''
        Returns parser used when all values are reported as floats.

        :param delimeter: The delimeter used in the file
        '''
        def parse(line):
            vals = line.strip().split(delimeter)
            return [float(x) if x.strip() else np.nan for x in line.split(delimeter)]
        return parse
    
    def parse_date_time_format(self, time_index: int,
                               delimeter: str = ''):
        '''
        Returns parser used when the time is reported as an absolute date.

        :param time_index: The index of the data column containing time data
        :param delimeter: The delimeter used in the file
        '''
        def parse(line):
            vals = line.strip().split(delimeter)
            date = vals[time_index]
            vals[time_index] = self.convert_absolute_time_to_elapsed_time(date)
            return [float(x) if x else np.nan for x in vals]
        return parse
    
    def record_data(self, line: str, parser: Callable[[str], List[float]]):
        '''
        Parses a line and adds the relevant data to the corresponding list in 
        self.data

        :param line: The line to be parsed
        :param parser: The function used to parse the line
        '''
        vals = parser(line)
        for data_name, val in zip(self.data_names, vals):
            self.data[data_name].append(val)

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
        