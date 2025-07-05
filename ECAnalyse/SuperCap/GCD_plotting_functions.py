from __future__ import annotations  # For type hinting self in class methods

from ..Experiment.Experiment import Experiment
from ..custom_plt import plt

from typing import TYPE_CHECKING, Optional, List
if TYPE_CHECKING:
    from ..File_Types import ECLab_File
    from matplotlib.axes import Axes

class GCD_Plotting_Mixin:
    '''
    Mixin class for GCD plotting functions
    '''
    def plot(
            self,
            ax: Optional[Axes] = None,
            labels: Optional[List[str]] = None,
            title: str = '',
            **kwargs
        ) -> Axes:
        '''
        Plots the GCD experiment data as Voltage vs Time

        :param ax: matplotlib Axes object to plot on. If None then uses current
            active Axes.
        :param labels: List of labels for each file. If None then no labels.
        :param title: Title for the plot
        :param kwargs: Additional keyword arguments to pass to the plot
        '''
        if ax is None: ax = plt.gca()
        if labels is None: labels = [''] * len(self.files)
        if len(labels) != len(self.files):
            raise ValueError(
                "Number of labels must match number of files in the experiment"
            )
        # All files will be plotted in the same colour and default is black
        if 'color' not in kwargs:
            kwargs['color'] = 'black'
        # Plot each of the files in the experiment
        for file, label in zip(self.files, labels):
            ax.plot(file.t, file.E, label=label, **kwargs)
        # Set labels and title
        ax.set_xlabel('Time / s')
        ax.set_ylabel('Voltage / V')
        if title: ax.set_title(title)
        # Finally return the ax object
        return ax
    
    def plot_current(
            self,
            ax: Optional[Axes] = None,
            labels: Optional[List[str]] = None,
            title: str = '',
            **kwargs
        ) -> Axes:
        '''
        Plots the GCD experiment data as Current vs Time

        :param ax: matplotlib Axes object to plot on. If None then uses current
            active Axes.
        :param labels: List of labels for each file. If None then no labels.
        :param title: Title for the plot
        :param kwargs: Additional keyword arguments to pass to the plot
        '''
        if ax is None: ax = plt.gca()
        if labels is None: labels = [''] * len(self.files)
        if len(labels) != len(self.files):
            raise ValueError(
                "Number of labels must match number of files in the experiment"
            )
        # All files will be plotted in the same colour and default is black
        if 'color' not in kwargs:
            kwargs['color'] = 'black'
        # Plot each of the files in the experiment
        for file, label in zip(self.files, labels):
            ax.plot(file.t, file.I, label=label, **kwargs)
        # Set labels and title
        ax.set_xlabel('Time / s')
        ax.set_ylabel('Current / mA')
        if title: ax.set_title(title)
        # Finally return the ax object
        return ax