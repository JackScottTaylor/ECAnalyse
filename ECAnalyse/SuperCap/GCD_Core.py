from __future__ import annotations  # For type hinting self in class methods

from ..Experiment.Experiment import Experiment
from ..custom_plt import plt

from typing import TYPE_CHECKING, Optional, List
if TYPE_CHECKING:
    from ..File_Types import ECLab_File
    from matplotlib.axes import Axes

class GCD(Experiment):
    '''
    Class for holding GCD data and methods for analysing it.
    File must contain time, current and voltage data, if not then error will be
    raised.
    
    :param files: ECLab_Files corresponding to the GCD experiment
    '''
    def __init__(self, *files: ECLab_File):
        super().__init__(*files)
        if not self.files_have_required_data():
            raise ValueError(
                "All files must contain time, current and voltage data"
            )
        
    def files_have_required_data(self) -> bool:
        '''
        Checks if the files have the required data for GCD analysis.
        
        :return: True if files have time, current and voltage data, else False
        '''
        for file in self.files:
            if not all(hasattr(file, attr) for attr in ['t', 'E', 'I']):
                return False
        return True