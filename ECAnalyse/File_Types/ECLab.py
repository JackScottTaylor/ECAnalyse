'''
This module contains the ECLab_File class which inherits from Data and is used
for loading in data from ECLab files formatted as either .txt or .csv
'''

from ..Data import Data

import numpy as np
import datetime

from typing import List, Callable, Union

from scipy.integrate import cumulative_trapezoid

class ECLab_File(Data):
    '''
    ECLab_File class for reading and processing data from ECLab files.

    :param filepath: The path to the ECLab file to be read. This is optional
        such that an empty ECLab_File object can be created which is important
        for combining or splitting data later on.
    '''
    def __init__(self, filepath=None):
        # Initialise the parent Data class
        Data.__init__(self)
        # Set the attributes specific to ECLab files
        self.time_format = "%m/%d/%Y %H:%M:%S.%f"
        self.data_type = 'ECLab_File'
        self.t_data_name = 'time/s'

        # If file_name provied then extract the data from the file.
        if filepath: self.extract_data(filepath)
        # Set the common attributes for ECLab files.
        self.set_commonly_accessed_attributes()


    def set_commonly_accessed_attributes(self):
        '''
        For an ECLab file, the commonly accessed attributes are time/s, Ewe/V,
        I/mA cycle number and pressure.
        Data for these is stored in the attributes t, E, I, c and P respectively
        '''
        self.set_attributes(
            ['time/s',  'Ewe/V',    'I/mA', 'cycle number', 'Pressure/bar (on Analog In1)'],
            ['t',       'E',        'I',    'c',            'P']
        )


    def extract_data(self, filepath: str):
        '''
        Internally called function used to extract the data from either a .txt
        or .csv formatted file.

        :param filepath: The path to the ecported data file
        '''
        if    filepath.endswith('.txt'): self.extract_from_txt(filepath)
        elif  filepath.endswith('.csv'): self.extract_from_csv(filepath)
        else: raise Exception("File must be .txt or .csv")


    def extract_from_txt(self, filepath: str):
        '''
        Internally called function used to extract data from a .txt formatted 
        ECLab data file. 

        :param filepath: The path to the .txt formatted ECLab data file
        '''
        # The first line contains some mus and therefore is encoded with latin1
        # instead of the usual UTF-8
        with open(filepath, encoding='latin1') as file:
            # First read the data_names from the first line of the txt file.
            # The line ends in a newline character, so last element not counted
            # as data_name. Then initialise the data dictionary.
            data_names = file.readline().split('\t')[:-1]
            self.initialise_data_dict(data_names)

            # Time can either be reported as elapsed time or in absolute date
            # format. Here we determine from the first line the time format
            # and choose the correct extraction method accordingly.
            parser = self.parse_elapsed_time_format(delimeter='\t')
            time_data_found = self.t_data_name in data_names
            elapsed_time = True
            if time_data_found:
                time_index = data_names.index(self.t_data_name)
                line = file.readline()
                # If : in line then indicates time is in date format.
                if ':' in line.split('\t')[time_index]:
                    start_time_date = line.split('\t')[time_index]
                    # Convert the date to eapsed time so can then covert to a 
                    # datetime object and then set that as the start_time.
                    start_time = self.convert_elapsed_time_to_datetime(
                        self.convert_absolute_time_to_elapsed_time(
                        start_time_date
                    ))
                    self.set_start_time(start_time)
                    elapsed_time = False
                    parser = self.parse_date_time_format(time_index,
                                                         delimeter='\t')
                self.record_data(line, parser)
            
            # Using the correct parser, read in all of the data and save it.
            for line in file:
                self.record_data(line, parser)
                
        # Convert in to numpy arrays
        for data_name in self.data_names:
            self.data[data_name] = np.array(self.data[data_name])

        # If the time is in date format, then zero the time
        if time_data_found and not elapsed_time: self.zero_time()


    def extract_from_csv(self, filepath: str):
        '''
        Internally called function used to extract data from a .csv formatted 
        ECLab data file. 

        :param filepath: The path to the .csv formatted ECLab data file
        '''
        # The first line contains some mus and therefore is encoded with latin1
        # instead of the usual UTF-8
        with open(filepath, encoding='latin1') as file:
            # For csv files the first line is formatted
            # "Technique started on : ";03/21/2025 04:33:06.786
            # Calling convert_absolute_time_to_alapsed_time set this as the 
            # start time.
            start_time = file.readline().split(';')[-1]
            # Pad to make sure correct number of decimal points
            date_part, ms_part = start_time.split('.')
            # Assign to start_time and end_time
            start_time = f"{date_part}.{ms_part.strip().ljust(6, '0')}"
            start_time = self.convert_absolute_time_to_elapsed_time(start_time)
            start_time = self.convert_elapsed_time_to_datetime(start_time)
            self.set_start_time(start_time)

            # The data names are on the next line separated by semicolons
            data_names = file.readline().split(';')
            # Remove quotation marks
            data_names = [x.replace('"', '').strip() for x in data_names]
            self.initialise_data_dict(data_names)

            # Time can either be reported as elapsed time or in absolute date
            # format. Here we determine from the first line the time format
            # and choose the correct extraction method accordingly.
            parser = self.parse_elapsed_time_format(delimeter=';')
            time_data_found = self.t_data_name in data_names
            if time_data_found:
                time_index = data_names.index(self.t_data_name)
                line = file.readline()
                if ':' in line.split(';')[time_index]:
                    parser = self.parse_date_time_format(time_index,
                                                         delimeter=';')
                self.record_data(line, parser)
            
            # Using the correct parser, read in all of the data and save it.
            for line in file:
                self.record_data(line, parser)
                
        # Convert in to numpy arrays
        for data_name in self.data_names:
            self.data[data_name] = np.array(self.data[data_name])

        # In the .csv files the start_time at the top of the file is start
        # time of the technique in the file but the time data is in elapsed
        # time from the start of the experiment. We would like start_time 
        # to correspond to start of the technique, so we zero the time but
        # don't change the start_time.
        if time_data_found:
            self.data[self.t_data_name] -= self.data[self.t_data_name][0]


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
        data_names = [x.rstrip()          for x in data_names]
        # Create empty list in self.data for each data name
        for name in data_names: self.data[name] = []


    def parse_elapsed_time_format(
            self,
            delimeter: str = '',
            ) -> Callable[[str], List[float]]:
        '''
        Returns parser used when all values are reported as floats.

        :param delimeter: The delimeter used in the file
        :return: A function that takes a line of text and returns a list of 
                 floats, with empty values replaced by NaN.
        '''
        def parse(line):
            vals = line.strip().split(delimeter)
            vals = self.comma_decimal_to_point_decimal(vals)
            return [float(x) if x.strip() else np.nan for x in vals]
        return parse
    

    def parse_date_time_format(
            self,
            time_index: int,
            delimeter:  str = ''
            ) -> Callable[[str], List[float]]:
        '''
        Returns parser used when the time is reported in date format.

        :param time_index: The index of the data column containing time data
        :param delimeter: The delimeter used in the file
        :return: A function that takes a line of text and returns a list of 
                 floats, with empty values replaced by NaN. Time is converted
                 to elapsed time.
        '''
        def parse(line):
            vals = line.strip().split(delimeter)
            vals = self.comma_decimal_to_point_decimal(vals)
            date = vals[time_index]
            vals[time_index] = ''
            elapsed_time = self.convert_absolute_time_to_elapsed_time(date)
            parsed = [float(x) if x.strip() else np.nan for x in vals]
            parsed[time_index] = elapsed_time
            return parsed
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


    def cycle(self, c: Union[int, float]) -> 'ECLab_File':
        '''
        Method to return ECLab_File object containing only the data from a 
        specific cycle. If cycle data not found then raise error.

        :param c: The desired cycle number
        :return: ECLab_File object containing only specified cycle.
        '''
        if not isinstance(c, (int, float)):
            raise TypeError(
                f'Cycle number must be an int or float, not {type(c)}.'
            )
        if not hasattr(self, 'c'):
            raise AttributeError(
                'Cycle number data not found in ECLab_File. '
                'Please check the file format.'
            )
        c = float(c)
        return self.in_data_range('c', c, c)


    def cycles(self, *cycles: Union[int, float]) -> 'ECLab_File':
        ''' 
        Returns ECLab_File containing data from the specified cycles.

        :param cycles: A variable number of cycle numbers to be included in the
            returned ECLab_File object.
        :return: ECLab_File object containing data from the specified cycles.
        '''
        if not hasattr(self, 'c'):
            raise AttributeError(
                'Cycle number data not found in ECLab_File. '
                'Please check the file format.'
            )
        
        cycles_list = list(cycles)
        if not cycles_list:
            raise ValueError(
                'No cycles provided. Please provide at least one cycle number.'
            )
        
        # Find the maximum cycle number in self
        max_self_cycle = np.max(self.c)
        # Go through the cycles_list and mod the cycle numbers so that -1 will
        # correspond to the last cycle for example
        cycles_list = [c % max_self_cycle for c in cycles_list]

        # Initialise empty Data object same type as self
        cycles_file = type(self)()
        # Create empty data dictionary with the same data names as self
        for data_name in self.data_names:
            cycles_file.data[data_name] = np.array([])
        # Go through the cycles_list in order and add the Data objects
        for c in cycles_list:
            cycles_file += self.cycle(c)
        
        # Set the common attributes of the new object.
        cycles_file.set_commonly_accessed_attributes()
        return cycles_file
    

    def calculate_cumulative_charge(self):
        '''
        Calculates the cumulative charge passed via integration of the current
        against time using the trapezoidal rule. The results is stored in 
        self.data['cumulative charge/C'] and under the attribute self.Q
        '''
        if not hasattr(self, 'I'):
            raise AttributeError(
                'To calculate cumulative charge, ECLab_File must contain ' \
                'current data in mA under the attribute self.I'
            )
        if not hasattr(self, 't'):
            raise AttributeError(
                'To calculate cumulative charge, ECLab_File must contain ' \
                'time data in seconds under the attribute self.t'
            )
        # Calculate the cumulative charge using the trapezoidal rule
        self.data['cumulative charge/C'] = cumulative_trapezoid(
            self.I, self.t, initial=0.0) / 1000 # Convert mAs to C
        
        # Set the attribute self.Q to the same data
        self.Q = self.data['cumulative charge/C']


    def calculate_power(self):
        '''
        Calculates power as the product of voltage and current. The results is
        stored in self.data['power/W'] and under the attribute self.P
        '''
        if not hasattr(self, 'E'):
            raise AttributeError(
                'To calculate power, ECLab_File must contain voltage data in V ' \
                'under the attribute self.E'
            )
        if not hasattr(self, 'I'):
            raise AttributeError(
                'To calculate power, ECLab_File must contain current data in mA ' \
                'under the attribute self.I'
            )
        # Calculate power as voltage multiplied by current
        self.data['power/W'] = (self.E * self.I) / 1000


    def calculate_cumulative_energy(self):
        '''
        Calculates cumulative energy as the integral of power against time where
        power is calculated as voltage multiplied by current
        '''
        pass

        
        
        