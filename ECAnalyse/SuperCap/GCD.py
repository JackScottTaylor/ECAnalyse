from __future__ import annotations  # For type hinting self in class methods

from ..Experiment.Experiment import Experiment
from ..custom_plt import plt, fig_h, fig_w

from datetime import datetime

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
                 file_labels: Optional[List[str]] = None,
                 mass1: Union[float, List[float]] = 0.0,
                 mass2: Union[float, List[float]] = 0.0):
        super().__init__(*files)

        # Stores the mass of the first and second electrode, if a list is 
        # provided then the average over all values is taken.
        if type(mass1) == List: self.mass1 = sum(mass1) / len(mass1)
        else:                   self.mass1 = mass1
        if type(mass2) == List: self.mass2 = sum(mass2) / len(mass2)
        else:                   self.mass2 = mass2

        # If file_labels provided, then store them, otherwise store list of 
        # empty strings
        if file_labels is None:
            self.file_labels = [''] * len(self.files)
        elif len(file_labels) != len(self.files):
            raise ValueError("Number of file labels must match number of files " \
                             "in the GCD experiment")
        else:
            self.file_labels = file_labels

    
    def plot(self, ax: Optional[Axes] = None, labels: Optional[List[str]] = None,
             resize: bool = True, size: tuple = (fig_w*2, fig_h),
             fig: Optional[Figure] = None, rolling: int = 1,
             plot_raw: bool = True, start_time: Optional[datetime] = None,
             **kwargs) -> Axes:
        '''
        Plots the GCD experiment data on the provided axes or the current axes.

        :param ax: The axes to plot on. If None, uses the current axes.
        :param labels: Optional list of labels for the plot.
        :param resize: If True, resizes the figure to the specified size.
        :param_size: Size of the figure if resize is True, defaults to full
            page width.
        :param fig: The figure to plot on. If None, uses the current figure.
        :param rolling: The window size for the rolling average, defaults to 1
            (no rolling average).
        :param plot_raw: If True and rolling > 1, then plots the raw data in 
            same colour but slightly transparent.
        :param start_time: If provided, sets the start time for the plot.
            If None, uses the earliest start time from the files.
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

        # All files plotted in the same colour.
        if 'color' not in kwargs:
            kwargs['color'] = 'black'
        if plot_raw:
            if rolling > 1: kwargs['alpha'] = 0.25
            # For each file in the GCD experiment, plot voltage against time.
            for file, label in zip(self.files, labels):
                deltaT = 0.0
                if start_time is not None:
                    deltaT = (file.start_time - start_time).total_seconds()
                ax.plot(file.t+deltaT, file.E, label=label, **kwargs)
        if rolling >1:
            kwargs['alpha'] = 1.0
            # For each file in the GCD experiment, plot the rolling average of
            # voltage against time.
            for file, label in zip(self.files, labels):
                deltaT = 0.0
                if start_time is not None:
                    deltaT = (file.start_time - start_time).total_seconds()
                t_av, E_av = file.rolling_average('t', 'E', w=rolling)
                ax.plot(t_av+deltaT, E_av, label=label, **kwargs)

        # Set the axes labels and title.
        ax.set_xlabel('Time / s')
        ax.set_ylabel('Voltage / V')
        return ax
    
    def plot_all_files(self, figsize: tuple = (fig_w*2, fig_h),
                       rolling: int = 1, plot_raw: bool = True,
                       **kwargs) -> None:
        '''
        Creates a new plot and displays it for all the files stored in the GCD
        experiment.
        
        Iterates through all the files and for each creates a new GCD object
        and uses the plot method. The title of each plot is set to label
        provided.

        :param figsize: Size of the figure to create, defaults to full page width.
        :param rolling: The window size for the rolling average, defaults to 1
            (no rolling average).
        :param plot_raw: If True and rolling > 1, then plots the raw data in
            same colour but slightly transparent.
        :param kwargs: Additional keyword arguments for the plot.
        '''
        for file, label in zip(self.files, self.file_labels):
            slice_GCD = GCD(file, file_labels=[label],
                            mass1=self.mass1, mass2=self.mass2)
            fig, ax = plt.subplots(figsize=figsize)
            slice_GCD.plot(ax=ax, labels=[label], resize=False,
                           rolling=rolling, plot_raw=plot_raw, **kwargs)
            ax.set_title(label)
            plt.show()


    def slice_data(self, cycle_over: dict[str, int]) -> dict[str, GCD]:
        '''
        Slices the GCD data by cycle number and returns dictionary of GCD
        objects with corresponding keys.
        
        cycle_over is dictionary where keys are used to distinguish different
        between different sections of the GCD and the provided values represent
        the cycle number of the last cycle in that section.
        
        For example, if cycle_over = {'charge': 10, 'discharge': 20}, then
        the returned dictionary will contain two GCD objects:
        - 'charge': GCD object containing cycles 1 to 10
        - 'discharge': GCD object containing cycles 11 to 20

        :param cycle_over: Dictionary where keys are used to distinguish
            different sections of the GCD and the provided values represent
            the cycle number of the last cycle in that section.
        :type cycle_over: dict[str, int]
        :return: Dictionary of GCD objects with corresponding keys.
        :rtype: dict[str, GCD]
        :raises ValueError: If more that one file is provided to the GCD
        '''
        if len(self.files) > 1:
            raise ValueError("Slicing data is only supported for single file " \
                             "GCD experiments.")
        file = self.files[0]
        sliced_data = {}
        first_cycle = 1
        for section, last_cycle in cycle_over.items():
            sliced_file = file.cycle_range(first_cycle, last_cycle)
            sliced_data[section] = GCD(sliced_file, file_labels=[section],
                                       mass1=self.mass1, mass2=self.mass2)
            first_cycle = last_cycle + 1
        return sliced_data
