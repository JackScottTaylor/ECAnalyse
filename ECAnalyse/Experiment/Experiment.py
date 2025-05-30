'''
This class is made to store functions and Data objects relevant for a specific
experiment.
'''
from ..Data import Data
import datetime

from typing import Optional, List

class Experiment:
    '''
    General class for holding experiment data

    :param files: Data objects that are part of the experiment
    :type files: Data
    '''
    def __init__(self, *files: Data):
        self.files = [file for file in files]
        # Initialise the start_time as None, if it required then global start
        # time can be calculated from the files.

        # If one file provided then set self.file to that file and set the
        # start_time to file's start_time.
        if len(self.files) == 1:
            self.file = self.files[0]
            self.start_time = self.file.start_time
        else:
            self.start_time = datetime.datetime.now()

    def sync_times(self):
        '''
        Syncs up the start time of all files in the experiment.

        This function sets the start time of all the files in the experiment to
        the earliest start time found and changes the elapsed time of each file
        accordingly.
        '''
        # Go through all the files and find if they have a start_time set
        start_times = []
        for file in self.files:
            if type(file.start_time) == datetime.datetime:
                start_times.append(file.start_time)

        # If datetimes found, then set the start_time to the earliest one.
        if start_times:
            self.start_time = min(start_times)

        # Go through the files and if they have a start_time set then set it to 
        # the experiment start_time and adjust the elapsed time accordingly.
        for file in self.files:
            if type(file.start_time) != datetime.datetime: continue
            delta_T = file.start_time - self.start_time
            delta_T_seconds = delta_T.total_seconds()
            file.start_time = self.start_time
            file.t += delta_T_seconds

    def all_files_contain(self, *data_names: str) -> bool:
        '''
        Check if all files in the experiment contain the specified data name.
        
        :param data_name: The name of the data to check for in all files.
        :return: True if all files contain the data name, False otherwise.
        '''
        # Use the data_key method of the Data class which raises an error if the
        # data cannot be found
        for file in self.files:
            for data_name in data_names:
                try: file.data_key(data_name)
                except ValueError: return False     
        return True   
