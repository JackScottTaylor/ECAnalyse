'''
This class is made to store functions and Data objects relevant for a specific
experiment.
'''
from ..Data import Data
import datetime

class Experiment:
    '''
    General class for holding experiment data
    '''
    def __init__(self, *files: Data):
        self.files = [file for file in files]

        # Each file should have an associated start_time
        # therefore we search for the earliest start_time, set this as global,
        # and then store an elapsed_start_time for each file.
        self.start_time = datetime.datetime.now()
        for file in files:
            assert file.start_time != 0, "NO START TIME DETECTED"
            if file.start_time < self.start_time:
                self.start_time = file.start_time
        
        for file in files:
            elapsed_start_time = file.start_time - self.start_time
            elapsed_start_time_s = elapsed_start_time.total_seconds()
            file.start_time = self.start_time
            file.t = file.t + elapsed_start_time_s