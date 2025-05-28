from __future__ import annotations  # For type hinting self in class methods

from ..Experiment.Experiment import Experiment
from ..custom_plt import plt

from typing import TYPE_CHECKING, Optional, List
if TYPE_CHECKING:
    from ..File_Types import ECLab_File
    from matplotlib.axes import Axes

class GCD(Experiment):
    '''
    Class for handling a GCD (Galvanostatic Charge-Discharge) experiment.
    
    :param files: ECLab_File objects that make up the GCD experiment.
    '''
    def __init__(self, *files: ECLab_File):
        super().__init__(*files)

    def all_files_contain(self, *data_names: str) -> bool:
        '''
        Check if all files in the GCD experiment contain the specified data name.
        
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

    def plot(self, ax: Optional[Axes] = None, labels: Optional[List[str]] = None,
             **kwargs) -> Axes:
        '''
        Plots the GCD experiment data on the provided axes or the current axes.

        :param ax: The axes to plot on. If None, uses the current axes.
        :param labels: Optional list of labels for the plot.
        :param kwargs: Additional keyword arguments for the plot.
        :return: The axes with the plot.
        :raises ValueError: If the files do not contain the required data.
        :raises ValueError: If the number of labels does not match the number
            of files.
        '''
        # Check that all files contain both time and voltage data.
        if not self.all_files_contain('t', 'E'):
            raise ValueError("All files must contain time and voltage data, " \
                             "which should be stored as 't' and 'E' " \
                             "attributes of the Data object")
        # If labels not provided, then create a list of empty strings
        # If labels provided, check that correct number provided.
        if labels is None:
            labels = [''] * len(self.files)
        elif len(labels) != len(self.files):
            raise ValueError("Number of labels must match number of files in " \
                             "the GCD experiment")
        # If no axes provided, then use the current axes.
        if ax is None: ax = plt.gca()

        # Sync the times of all the files in the experiment
        self.sync_times()

        # All files plotted in the same colour.
        if 'color' not in kwargs:
            kwargs['color'] = 'black'
        # For each file in the GCD experiment, plot voltage against time.
        for file, label in zip(self.files, labels):
            ax.plot(file.t, file.E, label=label, **kwargs)
        # Set the axes labels and title.
        ax.set_xlabel('Time / s')
        ax.set_ylabel('Voltage / V')
        return ax