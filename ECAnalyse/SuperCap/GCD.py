from __future__ import annotations  # For type hinting self in class methods

from .GCD_plotting_functions import GCD_Plotting_Mixin
from .GCD_Core import GCD as GCD_Core

from ..Experiment.Experiment import Experiment
from ..custom_plt import plt

from typing import TYPE_CHECKING, Optional, List
if TYPE_CHECKING:
    from ..File_Types import ECLab_File
    from matplotlib.axes import Axes

class GCD(GCD_Core, GCD_Plotting_Mixin):
    '''
    Class for holding GCD data and methods for analysing it.
    File must contain time, current and voltage data, if not then error will be
    raised.
    
    :param files: ECLab_Files corresponding to the GCD experiment
    '''
    pass
    

