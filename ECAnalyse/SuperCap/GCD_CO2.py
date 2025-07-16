'''
This class holds an Experiment type object for analysing a GCD experiment 
combined with CO2 data.
'''

from ..Experiment import Experiment
from ..File_Types import CO2_File
from .GCD import GCD
from ..custom_plt import plt
from ..custom_plt.plotting_functions import rolling_average_plot

from typing import TYPE_CHECKING, Optional, List
if TYPE_CHECKING:
    from matplotlib.Axes import Axes

    
class GCD_CO2(Experiment):
    '''
    Class for holding GCD data and CO2 data and for analysing the two together.
    
    :param GCD_exp: GCD Data object
    :param CO2_exp: CO2 Data object
    '''
    def __init__(
            self,
            GCD_exp: GCD,
            CO2_exp: CO2_File
        ) -> None:
        # Check that files are of correct type
        if not isinstance(GCD_exp, GCD):
            raise TypeError(
                f"GCD_exp must be of type GCD, not {type(GCD_exp).__name__}"
            )
        if not isinstance(CO2_exp, CO2_File):
            raise TypeError(
                f"CO2_exp must be of type CO2_File, not {type(CO2_exp).__name__}"
            )
        
        # Initialise the parent class with the given parameters
        # This should also sync up all of the times of the files
        super().__init__(GCD_exp, CO2_exp)

        # Save the GCD and CO2 files as attributes
        self.GCD: GCD       = GCD_exp
        self.CO2: CO2_File  = CO2_exp

    
    def plot(
            self,
            ax: Optional['Axes'] = None,
            CO2_ymin: Optional[float] = None,
            CO2_ymax: Optional[float] = None,
            CO2rolling_average_window: int = 10,
            GCD_color: str = 'black',
            CO2_color: str = 'royalblue'    
        ) -> 'Axes':
        '''
        Plots the GCD experiment as Voltage vs time and on the same figure with
        a shared time axis plots CO2 concentration against time. The time limits
        of the CO2 plot are set to the same as the GCD plot.
        '''
        if ax is None: ax = plt.gca()
        # Plot the GCD data
        ax = self.GCD.plot(ax=ax, color=GCD_color)
        # Save the x limits
        x_limits = ax.get_xlim()
        # Create second axis with shared x-axis to plot the CO2 data
        ax2 = ax.twinx()
        # Plot the CO2 data on the second axis
        rolling_average_plot(ax2, self.CO2, 't', 'CO2', rolling_average=True,
                             window_size=CO2rolling_average_window,
                             color=CO2_color)
        # Reset the x limits
        ax2.set_xlim(x_limits)
        # Set the y label for the CO2 axis
        ax2.set_ylabel('CO$_2$ concentration / %')

        # Set the y limits for the CO2 axis if specified
        ax2.set_ylim(CO2_ymin, CO2_ymax)

        return ax, ax2


    def export_CO2_to_txt(self, file_name: str) -> None:
        '''
        Exports the CO2 data in the region of the GCD experiment to a .txt file
        
        :param file_name: The name of the file to export to
        '''
        # Get the time limits of the GCD experiment
        start, end = self.GCD.start_time, self.GCD.end_time
        # Get the CO2 data in the region of the GCD experiment
        CO2_in_time_region = self.CO2.in_time_range(start, end)
        # Open the file for writing
        with open(file_name, 'w') as file:
            # Write the header
            file.write('time/s\tCO2/%\n')
            # Write the data
            for t, CO2 in zip(
                CO2_in_time_region.t, CO2_in_time_region.CO2
            ):
                file.write(f"{t}\t{CO2}\n")

