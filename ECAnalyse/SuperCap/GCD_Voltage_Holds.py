'''
This class is specifically for handling supercapacitor GCD experiments which 
include voltage holds and no zero current regions. It is a child of the
GCD class.
'''

from .GCD import GCD

from typing import Optional, List

class GCD_Voltage_Holds(GCD):
    '''
    Class for holding GCD data and methods for analysing it, specifically for
    experiments that include voltage holds.
    
    :param files: ECLab_Files corresponding to the GCD experiment
    '''
    
    def __init__(
            self,
            filepath: Optional[str] = None,
            mass1:            float = 0.0,
            mass2:            float = 0.0
        ):
        # Initialise the parent class with the given parameters
        super().__init__(
            filepath=filepath,
            mass1=mass1,
            mass2=mass2
        )

    def detect_regions(
            self
        ):
        '''
        Detects the charging, discharging, and voltage hold regions in the GCD
        '''
        self.detect_current_regions(
            min_region_length = 5,
            zero_threshold = 0.1
        )
        