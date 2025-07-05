'''
This class is made to store functions and Data objects relevant for a specific
experiment.
'''
from ..Data import Data, TIME_PLACEHOLDER
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
        self.start_time: datetime.datetime = TIME_PLACEHOLDER

    def sync_times(self):
        '''
        Syncs up the start time of all files in the experiment.

        This function sets the start time of all the files in the experiment to
        the earliest start time found and changes the elapsed time of each file
        accordingly.
        '''
        # Go through all the files and find if they have a start_time set
        start_times = []
        for file in self.files: start_times.append(file.start_time)

        # If datetimes found, then set the start_time to the earliest one.
        if start_times: self.start_time = min(start_times)

        # Go through the files and if they have a start_time set then set it to 
        # the experiment start_time and adjust the elapsed time accordingly.
        for file in self.files:
            file.shift_start_time(self.start_time)
