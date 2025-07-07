from __future__ import annotations  # For type hinting self in class methods

from ..custom_plt import plt, rolling_average_plot

from typing import TYPE_CHECKING, Optional, List
if TYPE_CHECKING:
    from ..File_Types import ECLab_File
    from matplotlib.axes import Axes
    from numpy import ndarray

class GCD_Plotting_Mixin:
    '''
    Mixin class for GCD plotting functions
    '''
    def plot(
            self,
            ax: Optional[Axes] = None,
            title: str = '',
            rolling_average: bool = False,
            window_size: int = 10,
            **kwargs
        ) -> Axes:
        '''
        Plots the GCD experiment data as Voltage vs Time

        :param ax: matplotlib Axes object to plot on. If None then uses current
            active Axes.
        :param title: Title for the plot
        :param rolling_average: If True, applies a rolling average to the data
        :param window_size: Size of the rolling average window if using
        :param kwargs: Additional keyword arguments to pass to the plot
        '''
        if ax is None: ax = plt.gca()

        ax = rolling_average_plot(
                ax, self, 't', 'E', rolling_average=rolling_average,
                window_size=window_size, **kwargs
                )

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
            rolling_average: bool = False,
            window_size: int = 10,
            **kwargs
        ) -> Axes:
        '''
        Plots the GCD experiment data as Current vs Time

        :param ax: matplotlib Axes object to plot on. If None then uses current
            active Axes.
        :param title: Title for the plot
        :param rolling_average: If True, applies a rolling average to the data
        :param window_size: Size of the rolling average window if using
        :param kwargs: Additional keyword arguments to pass to the plot
        '''
        if ax is None: ax = plt.gca()

        # Plot each of the files in the experiment
        ax = rolling_average_plot(
                ax, self, 't', 'I', rolling_average=rolling_average,
                window_size=window_size, **kwargs
                )
            
        # Set labels and title
        ax.set_xlabel('Time / s')
        ax.set_ylabel('Current / mA')
        if title: ax.set_title(title)
        # Finally return the ax object
        return ax


    def plot_capacitance_vs_E(
        self,
            ax: Optional[Axes] = None,
            labels: Optional[List[str]] = None,
            title: str = '',
            rolling_average: bool = False,
            window_size: int = 10,
            **kwargs
        ) -> Axes:
        '''
        This function plots the capacitance (cumulative charge per charge / 
        discharge cycle) against the voltage for each file in the GCD exp

        :param ax: matplotlib Axes object to plot on. If None then uses current
            active Axes.
        :param labels: List of labels for each file. If None then no labels.
        :param title: Title for the plot
        :param rolling_average: If True, applies a rolling average to the data
        :param window_size: Size of the rolling average window if using
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
        
        sections = self.charge_discharge_sections()
        for section in sections:
            Q = section.cumulative_charge()
            E = section.E
            ax = rolling_average_plot(
                ax, section, 'E', 'Q', rolling_average=rolling_average,
                window_size=window_size, **kwargs
            )


    def plot_charging_regions(
            self,
            ax: Optional[Axes] = None,
            **kwargs
        ) -> Axes:
        '''
        Plots the voltage profile against time, however colours the regions it
        has detected as either charging, discharging or zero in different 
        colours.

        :param ax: matplotlib Axes object to plot on. If None then uses current
            active Axes.
        :param kwargs: Additional keyword arguments to pass to the plot
        '''
        if ax is None: ax = plt.gca()

        for region in self.detected_switch_regions:
            _, charging_parity, i1, i2 = region
            kwargs['color'] = 'black'
            if   charging_parity == 'positive': kwargs['color'] = '#DC267F'
            elif charging_parity == 'negative': kwargs['color'] = '#648FFF'
            if i2 == len(self.t) - 1: i2 = None
            ax.plot(
                self.t[i1:i2], self.E[i1:i2], **kwargs
            )

        # Set axis labels
        ax.set_xlabel('Time / s')
        ax.set_ylabel('Voltage / V')

        # Create a legend
        handles = []
        for parity, color in zip(
            ['Charging', 'Discharging', 'Zero Current'],
            ['#DC267F', '#648FFF', 'black']
        ):
            handles.append(plt.Line2D([0], [0], color=color, lw=2, label=parity))
        ax.legend(handles=handles, title='Charging Parity')

        return ax
    

    def plot_charge_discharge_cycles(
            self,
            ax: Optional[Axes] = None,
            **kwargs
        ) -> Axes:
        '''
        Plots the charge-discharge cycles detected in the GCD experiment.

        :param ax: matplotlib Axes object to plot on. If None then uses current
            active Axes.
        :param kwargs: Additional keyword arguments to pass to the plot
        '''
        if ax is None: ax = plt.gca()
        colours = plt.rcParams['axes.prop_cycle'].by_key()['color']
        ncolours = len(colours)

        for i, cycle in enumerate(self.detected_charge_discharge_cycles):
            kwargs['color'] = colours[i % ncolours]
            charging, discharging = cycle
            charging_i1, charging_i2 = charging[2], charging[3]
            discharging_i1, discharging_i2 = discharging[2], discharging[3]
            if discharging_i2 == len(self.t) - 1:
                discharging_i2 = None
            charging_t, charging_E = self.t[charging_i1:charging_i2], self.E[charging_i1:charging_i2]
            discharging_t, discharging_E = self.t[discharging_i1:discharging_i2], self.E[discharging_i1:discharging_i2]
            ax.plot(charging_t, charging_E, **kwargs)
            ax.plot(discharging_t, discharging_E, **kwargs)

        # Set axis labels
        ax.set_xlabel('Time / s')
        ax.set_ylabel('Voltage / V')

        return ax



