from ..Data import Data

import numpy as np

class CO2_File(Data):
    '''
    Used to extract the data from a CO2 sensor file.

    :Parent Class Data:
    '''
    def __init__(self, *file_name: str):
        '''
        If file_name is provided then reads the data.
        
        :param file_name: The path of the file to be read
        '''
        Data.__init__(self)
        self.time_format = "%Y-%m-%d %H:%M:%S.%f"
        self.data_type = 'CO2_File'
        self.t_data_name = 'time/s'

        if file_name: self.extract_data(file_name[0])
        self.set_commonly_accessed_attributes()

    def set_commonly_accessed_attributes(self):
        '''
        Sets the read data as attributes of the object
        '''
        self.set_attributes(
            ['time/s',  'CO2/%'],
            ['t',       'CO2']
        )

    def extract_data(self, file_name: str):
        '''
        Reads the data from the file and stores it in the self.data dictionary.

        :param file_name: The path of the CO2 txt file to be read.
        '''
        assert file_name.endswith('.txt'), "File must be a .txt file"
        # Set the self.data dictionary keys
        self.data_names = ['time/s', 'CO2/%']
        self.data = {name: [] for name in self.data_names}

        # Read the data from the file
        with open(file_name, 'r') as file:
            for line in file:
                if line.strip() == '': continue
                date, CO2 = line.split(',')
                try:
                    self.data['time/s'].append(
                        self.convert_absolute_time_to_elapsed_time(date)
                    )
                    self.data['CO2/%'].append(float(CO2.strip()))
                except: continue

        # Convert data to numpy arrays
        self.data['time/s'] = np.array(self.data['time/s'])
        self.data['CO2/%']  = np.array(self.data['CO2/%'])

        # Set the end time
        self.end_time = self.convert_elapsed_time_to_datetime(
            self.data['time/s'][-1]
        )
