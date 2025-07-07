from __future__ import annotations  # For type hinting self in class methods

from ..File_Types import ECLab_File
import numpy as np
import warnings

from typing import TYPE_CHECKING, Optional, List
if TYPE_CHECKING:
    from ..File_Types import ECLab_File
    from matplotlib.axes import Axes
    from ..Data import Data

'''
This class is made for the analsysis of GCD experiments for supercap systems.
As this is the most basic version there is only electrochemical data present and
therefore this class will be made a child of the ECLab_File class. 

It will be loaded directly from a filepath like other Data type objects.
'''

class GCD(ECLab_File):
    '''
    Class for holding GCD data and methods for analysing it.
    File must contain time, current and voltage data, if not then error will be
    raised.
    
    :param filepath: Filepath to the GCD data file. If None, no file laoded
    :param mass1: Mass of the first electrode in mg (default is 0.0)
    :param mass2: Mass of the second electrode in mg (default is 0.0)
    '''
    def __init__(
            self,
            filepath: Optional[str] = None,
            mass1:            float = 0.0,
            mass2:            float = 0.0
        ):
        super().__init__(filepath=filepath)
        self.mass1 = mass1
        self.mass2 = mass2
        # Check that required data is present
        self.verify_required_data_present()
        # initialise the detected regions cache as None
        self.detected_current_regions_cache         = None
        self.detected_switch_regions_cache          = None
        self.detected_charge_discharge_cycles_cache = None


    @property
    def detected_current_regions(self) -> List[tuple]:
        '''
        Returns the detected regions in the form of a list of tuples where each
        tuple is formatted as (positive/negative/zero, start_index, end_index).
        
        If the regions have not yet been detected, then detection method is 
        called and the regions are cached
        
        :return List of tuples with detected regions
        '''
        if self.detected_current_regions_cache is None:
            print(
                "------------------------WARNING------------------------\n"
                "Regions not yet detected. Detecting now with default \n"
                "parameters (zero_threshold=0.1, min_region_length=5). \n"
                "Best practice is to call self.detect_regions() \n"
                "with your own parameters before accessing this property.\n"
                "------------------------WARNING------------------------\n")
            self.detect_current_regions()
        return self.detected_current_regions_cache
    

    @property
    def detected_switch_regions(self) -> List[tuple]:
        '''
        Returns the detected switch regions in the form of a list of tuples
        where each tuple has format:
        (current_region, charging_profile, start_index, end_index)
        If the current region is 'zero' then charging_profile is None.

        :return List of tuples with detected regions
        '''
        if self.detected_switch_regions_cache is None:
            print(
                "------------------------WARNING------------------------\n"
                "Switch regions not yet detected. Detecting now with \n"
                "default parameters (min_region_length=5). \n"
                "Best practice is to call self.detect_switch_regions() \n"
                "before accessing this property.\n"
                "------------------------WARNING------------------------\n")
            self.detect_switch_regions()
        return self.detected_switch_regions_cache
    

    @property
    def detected_charge_discharge_cycles(self) -> List[tuple]:
        '''
        Returns the detected charge-discharge cycles in the form of a list of
        tuples where each tuple has format:
        (charging_region, discharging_region)

        If the charge-discharge cycles have not yet been detected, detection
        method is called and the cycles are cached.

        :return List of tuples with detected charge-discharge cycles
        '''
        if self.detected_charge_discharge_cycles_cache is None:
            print(
                "------------------------WARNING------------------------\n"
                "Charge-discharge cycles not yet detected. Detecting now.\n"
                "Best practice is call self.detect_charge_discharge_cycles() \n"
                "before accessing this property.\n"
                "------------------------WARNING------------------------\n")
            self.detect_charge_discharge_cycles()
        return self.detected_charge_discharge_cycles_cache
    

    def verify_required_data_present(self) -> None:
        '''
        GCD files require time, current and voltage data. This method checks
        that these fields have been found and saves as attributes t, I and E
        respectively. If not found then error is raised.
        '''
        for attr in ['t', 'I', 'E']:
            if not hasattr(self, attr):
                raise ValueError(
                    f"GCD data files must contain '{attr}' data. "
                    "Please check the files and try again."
                )
            

    def detect_current_regions(
            self,
            zero_threshold: float = 0.1,
            min_region_length: int = 5
        ):
        '''
        This method detects regions of the GCD data where the current is either
        positive, negative, or zero. Zero current is defined as being between 
        -zero_threshold and zero_threshold. A region must also contain at least
        min_region_length data points to be considered a valid region. Detected
        regions are accessed via the `detected_regions` property. They are
        stored as a list of tuples in the format: 
        (region_type, start_index, end_index) where region_type is one of
        'positive', 'negative', or 'zero'. The start_index and end_index are the
        indices of the first and last data points in the region, respectively.
        If end_index corresponds to last data point, then it is saved as -1.
    
        :param zero_threshold: Threshold for defining zero current region
        :param min_region_length: Minimum length of a region to be considered
            valid
        '''
        self.detected_current_regions_cache = []
        I = self.I
        n = len(I)
        def region(value):
            if value > zero_threshold:
                return 'positive'
            elif value < -zero_threshold:
                return 'negative'
            else:
                return 'zero'
            
        current_region = region(I[0])
        region_start    = 0
        region_end      = 0

        def save_region_if_valid(region_start, region_end):
            if (region_end - region_start + 1) >= min_region_length:
                if region_end == n - 1:
                    region_end = -1
                self.detected_current_regions_cache.append(
                    (current_region, region_start, region_end)
                )

        for i, value in enumerate(I):
            if i == 0: continue
            if region(value) == current_region:
                region_end = i
            else:
                save_region_if_valid(region_start, region_end)
                current_region  = region(value)
                region_start    = i
                region_end      = i

        # Save the last region if valid
        save_region_if_valid(region_start, region_end)


    def detect_switch_regions(
            self,
            min_region_length: int = 5
            ):
        '''
        This method looks at the detected current regions and if the region is 
        actuallya switching profile, then splits in to two regions, charging
        and discharging. The switch happens when the voltage goes to zero.
        When current is negative, voltage should be moving more negative,
        therefore the first half would be discharging, and once the voltage
        moves past zero, the supercapacitor is charging again.

        :param min_region_length: Minimum length of a region to be considered
            valid. If a region is shorter than this, it will not be included in
            the detected regions.
        '''
        self.detected_switch_regions_cache = []
        n = len(self.t) - 1

        def save_region_if_valid(
                current_parity,
                charging_parity,
                region_start,
                region_end
                ):
            if (region_end - region_start + 1) >= min_region_length:
                if region_end == n:
                    region_end = -1
                self.detected_switch_regions_cache.append(
                    (current_parity, charging_parity, region_start, region_end)
                )

        def parity(value):
            if value > 0:
                return 'positive'
            elif value < 0:
                return 'negative'
            else:
                return 'zero'
            
        def E_to_charging_parity(E_parity, current_parity):
            if current_parity == 'positive':
                if E_parity == 'positive': return 'positive'
                if E_parity == 'negative': return 'negative'
            if current_parity == 'negative':
                if E_parity == 'positive': return 'negative'
                if E_parity == 'negative': return 'positive'
            if current_parity == 'zero':
                return 'Zero'


        for region in self.detected_current_regions:
            current_parity, start_index, end_index = region
            if end_index == -1: end_index = n
            if current_parity == 'zero':
                save_region_if_valid(
                    current_parity, 'zero', start_index, end_index
                )
                continue
            # If current is positive then we are charging initially
            E_parity = parity(self.E[start_index])
            sub_region_start = start_index
            sub_region_end = start_index
            for i in range(start_index+1, end_index + 1):
                if parity(self.E[i]) != E_parity:
                    # Calculate the charging parity
                    charging_parity = E_to_charging_parity(
                        E_parity, current_parity
                    )
                    # Save the region if valid
                    save_region_if_valid(
                        current_parity, charging_parity,
                        sub_region_start, sub_region_end
                    )
                    sub_region_start = i
                    sub_region_end = i
                    E_parity = parity(self.E[i])
                else:
                    sub_region_end = i
            
            # Save the last sub-region if valid
            charging_parity = E_to_charging_parity(
                E_parity, current_parity
            )
            save_region_if_valid(
                current_parity, charging_parity,
                sub_region_start, sub_region_end
            )


    def detect_charge_discharge_cycles(self):
        '''
        This requires that the switch regions have already been detected.
        A charge-discharge cycle is a charging region followed by a discharging
        region, possibly with a zero region inbetween.
        '''
        self.detected_charge_discharge_cycles_cache = []
        unused_regions = []
        current_cycle = []
        for region in self.detected_switch_regions:
            _, charging_parity, i1, i2 = region
            if len(current_cycle) == 0:
                if charging_parity == 'positive':
                    current_cycle.append(region)
                else:
                    unused_regions.append(region)
            
            else:
                if charging_parity == 'negative':
                    current_cycle.append(region)
                    self.detected_charge_discharge_cycles_cache.append(
                        current_cycle)
                    current_cycle = []
                else:
                    unused_regions.append(region)

        print(
            f"Detected {len(self.detected_charge_discharge_cycles)} "
            "charge-discharge cycles."
        )
        print(
            f"Detected {len(unused_regions)} unused regions that were not "
            f"part of a charge-discharge cycle. Of which there were" \
            f" {len([r for r in unused_regions if r[1] == 'positive'])} " \
            f"positive, " \
            f"{len([r for r in unused_regions if r[1] == 'negative'])} negative, " \
            f"and {len([r for r in unused_regions if r[1] == 'zero'])} zero."
        )

    
    def charge_discharge_cycle_times(self) -> np.ndarray:
        '''
        Calculates the charge-discharge cycle times using the detected 
        charge-discharge cycles. The cycle time is defined as the time between
        the start of the charging region and the end of the discharging region.

        :return: Numpy array of cycle times for each cycle
        '''
        cycle_times = np.empty(len(self.detected_charge_discharge_cycles))
        for i, cycle in enumerate(self.detected_charge_discharge_cycles):
            charging, discharging = cycle
            charging_i1, charging_i2 = charging[2], charging[3]
            discharging_i1, discharging_i2 = discharging[2], discharging[3]
            if discharging_i2 == -1:
                discharging_i2 = None

            cycle_times[i] = (
                self.t[discharging_i2] + self.t[charging_i1]
            ) / 2
        return np.abs(cycle_times)


    def Coulomb_efficiencies(self) -> np.ndarray:
        '''
        Calculates the charge-discharge cycle Coulomb efficiencies using the 
        detected charge-discharge cycles. The Coulomb efficiency is defined as
        discharged charge / charging charge, as a percentage.

        :return: Numpy array of Coulomb efficiencies for each cycle
        '''
        efficiencies = np.empty(len(self.detected_charge_discharge_cycles))
        if not hasattr(self, 'Q'):
            warnings.warn(
                "Cumulative charge does not appear to be calculated. \n" \
                "Now calculating using self.calculate_cumulative_charge().\n" \
                "Best practice is to call this method prior to trying to \n" \
                "calculate cycle efficiencies."
            )
            self.calculate_cumulative_charge()

        for i, cycle in enumerate(self.detected_charge_discharge_cycles):
            charging, discharging = cycle
            charging_i1, charging_i2 = charging[2], charging[3]
            discharging_i1, discharging_i2 = discharging[2], discharging[3]
            if discharging_i2 == -1:
                discharging_i2 = None

            Q_charging = self.Q[charging_i2] - self.Q[charging_i1]
            Q_discharging = self.Q[discharging_i2] - self.Q[discharging_i1]
            if Q_charging == 0:
                warnings.warn(
                    f"Cycle {i} has zero charging charge. "
                    "Coulomb efficiency will be set to NaN."
                )
                efficiencies[i] = np.nan
            else:
                efficiencies[i] = (
                    Q_discharging / Q_charging * 100.0
                )
        return np.abs(efficiencies)
    

    def energy_efficiencies(self) -> np.ndarray:
        '''
        Calculates the charge-discharge cycle energy efficiencies using the 
        detected charge-discharge cycles. The energy efficiency is defined as
        discharged energy / charging energy, as a percentage.

        :return: Numpy array of energy efficiencies for each cycle
        '''
        efficiencies = np.empty(len(self.detected_charge_discharge_cycles))
        if not hasattr(self, 'energy'):
            warnings.warn(
                "Cumulative energy does not appear to be calculated. \n" \
                "Now calculating using self.calculate_cumulative_energy().\n" \
                "Best practice is to call this method prior to trying to \n" \
                "calculate cycle efficiencies."
            )
            self.calculate_cumulative_energy()

        for i, cycle in enumerate(self.detected_charge_discharge_cycles):
            charging, discharging = cycle
            charging_i1, charging_i2 = charging[2], charging[3]
            discharging_i1, discharging_i2 = discharging[2], discharging[3]
            if discharging_i2 == -1:
                discharging_i2 = None

            energy_charging = self.energy[charging_i2] - self.energy[charging_i1]
            energy_discharging = self.energy[discharging_i2] - self.energy[discharging_i1]
            if energy_charging == 0:
                warnings.warn(
                    f"Cycle {i} has zero charging energy. "
                    "Energy efficiency will be set to NaN."
                )
                efficiencies[i] = np.nan
            else:
                efficiencies[i] = (
                    energy_discharging / energy_charging * 100.0
                )
        return np.abs(efficiencies)


    def resistances(self) -> np.ndarray:
        '''
        Calculates the resistance for each charge-discharge cycle using the 
        ohmic drop method. R = ΔV / ΔI, where ΔV is the voltage drop and 
        ΔI is the change in current. Voltage drop calculated as difference
        last voltage in charge region and first voltage in discharge region.
        ΔI is the change in current between the same two points.

        :return: Numpy array of resistances for each cycle in Ohms
        '''
        resistances = np.empty(len(self.detected_charge_discharge_cycles))
        for i, cycle in enumerate(self.detected_charge_discharge_cycles):
            charging, discharging = cycle
            charging_i1, charging_i2 = charging[2], charging[3]
            discharging_i1, discharging_i2 = discharging[2], discharging[3]
            if discharging_i2 == -1:
                discharging_i2 = None

            delta_V = self.E[discharging_i1] - self.E[charging_i2]
            delta_I = (self.I[discharging_i1] - self.I[charging_i2]) / 1000
            if delta_I == 0:
                warnings.warn(
                    f"Cycle {i} has zero change in current. "
                    "Resistance will be set to NaN."
                )
                resistances[i] = np.nan
            else:
                resistances[i] = np.abs(delta_V / delta_I)
        return resistances
            

            




        
