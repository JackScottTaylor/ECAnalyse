from __future__ import annotations  # For type hinting self in class methods

from ..Experiment.Experiment import Experiment
from ..custom_plt import plt, fig_h, fig_w

from typing import TYPE_CHECKING, Optional, List, Union
if TYPE_CHECKING:
    from ..File_Types import ECLab_File
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

class GCD(Experiment):
    '''
    Class for handling a GCD (Galvanostatic Charge-Discharge) experiment.
    
    :param files: ECLab_File objects that make up the GCD experiment.
    :type files: ECLab_File
    :param mass1: Mass of the first electrode in mg, defaults to 0.0.
    :type mass1: float or List[float], optional
    :param mass2: Mass of the second electrode in mg, defaults to 0.0.
    :type mass2: float or List[float], optional
    '''
    def __init__(self, *files: ECLab_File,
                 mass1: Union[float, List[float]] = 0.0,
                 mass2: Union[float, List[float]] = 0.0):
        super().__init__(*files)

        # Stores the mass of the first and second electrode, if a list is 
        # provided then the average over all values is taken.
        if type(mass1) == List: self.mass1 = sum(mass1) / len(mass1)
        else:                   self.mass1 = mass1
        if type(mass2) == List: self.mass2 = sum(mass2) / len(mass2)
        else:                   self.mass2 = mass2

    
    def plot(self, ax: Optional[Axes] = None, labels: Optional[List[str]] = None,
             resize: bool = True, size: tuple = (fig_w*2, fig_h),
             fig: Optional[Figure] = None,
             **kwargs) -> Axes:
        '''
        Plots the GCD experiment data on the provided axes or the current axes.

        :param ax: The axes to plot on. If None, uses the current axes.
        :param labels: Optional list of labels for the plot.
        :param resize: If True, resizes the figure to the specified size.
        :param_size: Size of the figure if resize is True, defaults to full
            page width.
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
        # If resize is True, then resizes the figure provided or the current
        # figure if figure is not provided.
        if resize:
            if fig is None: fig = plt.gcf()
            fig.set_size_inches(size[0], size[1])
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