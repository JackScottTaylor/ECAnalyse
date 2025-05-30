from __future__ import annotations  # For type hinting self in class methods

from ..Experiment.Experiment import Experiment
from ..custom_plt import plt, fig_h, fig_w

from datetime import datetime
from scipy.ndimage import gaussian_filter1d

import numpy as np

from typing import TYPE_CHECKING, Optional, List, Union
if TYPE_CHECKING:
    from ..File_Types import ECLab_File
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from numpy import ndarray

class GCD(Experiment):
    '''
    Class for handling a GCD (Galvanostatic Charge-Discharge) experiment.
    
    :param file: ECLab_File object that make up the GCD experiment.
    :type file: ECLab_File
    :param mass1: Mass of the first electrode in mg, defaults to 0.0.
    :type mass1: float or List[float], optional
    :param mass2: Mass of the second electrode in mg, defaults to 0.0.
    :type mass2: float or List[float], optional
    '''
    def __init__(self, file: ECLab_File,
                 file_label: str = '',
                 mass1: Union[float, List[float]] = 0.0,
                 mass2: Union[float, List[float]] = 0.0):
        super().__init__(file)

        # Stores the mass of the first and second electrode, if a list is 
        # provided then the average over all values is taken.
        if type(mass1) == List: self.mass1 = sum(mass1) / len(mass1)
        else:                   self.mass1 = mass1
        if type(mass2) == List: self.mass2 = sum(mass2) / len(mass2)
        else:                   self.mass2 = mass2

        # Save the file, label
        self.file_label = file_label

    
    def plot(self, ax: Optional[Axes] = None, label: str = '',
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
            raise ValueError("File must contain time and voltage data, " \
                             "which should be stored as 't' and 'E' " \
                             "attributes of the Data object")
        
        # If resize is True, then resizes the figure provided or the current
        # figure if figure is not provided.
        if resize:
            if fig is None: fig = plt.gcf()
            fig.set_size_inches(size[0], size[1])

        # If no axes provided, then use the current axes.
        if ax is None: ax = plt.gca()

        # Default colour is black.
        if 'color' not in kwargs:
            kwargs['color'] = 'black'

        # Calculate any required time shift.
        deltaT = 0.0
        if start_time is not None:
            deltaT = (self.start_time - start_time).total_seconds()

        # If plot_raw then plot the non-smoothed data.
        if plot_raw:
            # If rolling > 1 then plot slightly transparent.
            if rolling > 1: kwargs['alpha'] = 0.25
            ax.plot(self.file.t+deltaT, self.file.E, label=label, **kwargs)

        # If smoothing, then plot the smoothed data.
        if rolling >1:
            kwargs['alpha'] = 1.0
            ax.plot(self.file.t+deltaT, self.file.E, label=label, **kwargs)

        # Set the axes labels and title.
        ax.set_xlabel('Time / s')
        ax.set_ylabel('Voltage / V')
        return ax


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
        sliced_data = {}
        first_cycle = 1
        for section, last_cycle in cycle_over.items():
            sliced_file = self.file.cycle_range(first_cycle, last_cycle)
            sliced_data[section] = GCD(sliced_file, file_label=section,
                                       mass1=self.mass1, mass2=self.mass2)
            first_cycle = last_cycle + 1
        return sliced_data
    
    def positive_current(self) -> ECLab_File:
        '''
        From the associated GCD file, returns a new ECLab_File object containing
        only the parts of the GCD where the current is positive.
        
        :return: ECLab_File object containing only the parts of the GCD where
            the current is positive.
        :rtype: ECLab_File
        '''
        return self.file.in_data_range('I', 0, float('inf'))
    
    def negative_current(self) -> ECLab_File:
        '''
        From the associated GCD file, returns a new ECLab_File object containing
        only the parts of the GCD where the current is negative.
        
        :return: ECLab_File object containing only the parts of the GCD where
            the current is negative.
        :rtype: ECLab_File
        '''
        return self.file.in_data_range('I', float('-inf'), 0)
    
    def extract_sections_by_current_direction(self) -> List[ECLab_File]:
        '''
        Extracts the sections of the GCD data where the sign of the current
        does not change with time. We will say that positive counts as >= 0.
        '''
        sections = []
        previous_sign = self.file.I[0] >= 0
        section = [self.file.t[0], self.file.t[0]]
        for t, I in zip(self.file.t, self.file.I):
            sign = I >= 0
            if sign != previous_sign:
                sections.append(section)
                section = [t, t]
                previous_sign = sign
            section[1] = t
        sections.append(section)
        # Convert the sections to ECLab_File objects
        print(sections)
        return [self.file.in_time_range(float(section[0]), float(section[1]))
                for section in sections]
    
    def instantaneous_capacitance(self, gravimetric: bool = False,
                                  electrode: int = 0,
                                  w: int=5) -> ndarray:
        '''
        Calculates the capacitance at every time point in the GCD data.
        
        For a capacitor, Q=CV, where Q is the charge, C is the capacitance
        and V is the voltage. 
        Take the time derivative to get
        dQ/dt = C * dV/dt
        Therefore, C = dQ/dt / dV/dt.
        dQ/dt is the current, and dV/dt can be explicitly calculated at each
        point using finite differences.

        :param gravimetric: If True, then the capacitance is calculated
            gravimetrically, i.e. per gram of active material.
            Defaults to False.
        :param electrode: Describes which electrode to consider, 
            if set to 0, then only consider the whole cell. If set to 1 or 2
            then only consider the first or second electrode respectively.
        :param w: Smooths current data using a gaussian filter with sigma equal
            to w
        :return: Array of instantaneous capacitance values at each time point
            in F or Fg-1 depending on whether gravimetric requested.
        '''
        # Extract the two currents from the GCD data
        positive_current = self.positive_current()
        negative_current = self.negative_current()
        # Smooth the Voltage data using a gaussian filter
        pos_V = gaussian_filter1d(positive_current.E, w)
        neg_V = gaussian_filter1d(negative_current.E, w)
        # Calculate the time derivative of Voltage using np.gradient
        pos_dVdt = np.gradient(pos_V, positive_current.t)
        neg_dVdt = np.gradient(neg_V, negative_current.t)
        # Calculate the instantaneous capacitances
        pos_C = positive_current.I / pos_dVdt
        neg_C = negative_current.I / neg_dVdt
        # Determine the capacitance scaling factor
        C_scaling_factor = 1.0
        if gravimetric:
            if   electrode == 0: C_scaling_factor /= (self.mass1 + self.mass2 / 1000)
            elif electrode == 1: C_scaling_factor /= (self.mass1 / 1000)
            elif electrode == 2: C_scaling_factor /= (self.mass2 / 1000)
            else: raise ValueError("electrode must be 0, 1 or 2")
        else:
            if electrode == 0: pass
            elif electrode == 1 or electrode == 2: C_scaling_factor *= 2.0
            else: raise ValueError("electrode must be 0, 1 or 2")
        # Multiply the capacitances by the scaling factor
        pos_C *= C_scaling_factor
        neg_C *= C_scaling_factor
        # Concatenate the capacitances and time arrays
        all_capacitances = np.append(pos_C, neg_C)
        all_times        = np.append(positive_current.t, negative_current.t)
        # Sort the capacitances and times by time
        sorted_indices = np.argsort(all_times)
        sorted_capacitances = all_capacitances[sorted_indices]
        # Return the sorted capacitances
        return sorted_capacitances



        


    

