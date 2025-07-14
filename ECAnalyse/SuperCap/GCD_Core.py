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
        self.detected_charging_regions_cache        = None
        self.detected_charge_discharge_cycles_cache = None
        self.detected_voltage_hold_regions_cache    = None


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
    def detected_charging_regions(self) -> List[tuple]:
        '''
        Returns the detected charging regions in the form of a list of tuples
        where each tuple has format:
        (current_region, charging_profile, start_index, end_index)
        If the current region is 'zero' then charging_profile is None.

        :return List of tuples with detected regions
        '''
        if self.detected_charging_regions_cache is None:
            print(
                "------------------------WARNING------------------------\n"
                "charging regions not yet detected. Detecting now with \n"
                "default parameters (min_region_length=5). \n"
                "Best practice is to call self.detect_charging_regions() \n"
                "before accessing this property.\n"
                "------------------------WARNING------------------------\n")
            self.detect_charging_regions()
        return self.detected_charging_regions_cache
    

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
    

    @property
    def detected_voltage_hold_regions(self) -> List[tuple]:
        '''
        Returns the detected voltage hold regions in the form of a list of 
        tuples where each tuple has format:
        (hold_value, start_index, end_index)

        If the voltage hold regions have not yet been detected, detection
        method is called and the regions are cached.

        :return List of tuples with detected voltage hold regions
        '''
        if self.detected_voltage_hold_regions_cache is None:
            print(
                "------------------------WARNING------------------------\n"
                "Voltage hold regions not yet detected. Detecting now with \n"
                "default parameters (min_region_length=5, zero_threshold=0.001). \n"
                "Best practice is to call self.detect_voltage_hold_regions() \n"
                "before accessing this property.\n"
                "------------------------WARNING------------------------\n")
            self.detect_voltage_hold_regions()
        return self.detected_voltage_hold_regions_cache
    

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
        'POSITVE_CURRENT', 'NEGATIVE_CURRENT', or 'ZERO_CURRENT'.
        The start_index and end_index are the indices of the first and last data
        points in the region, respectively.
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
                return 'POSITIVE_CURRENT'
            elif value < -zero_threshold:
                return 'NEGATIVE_CURRENT'
            else:
                return 'ZERO_CURRENT'
            
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


    def detect_charging_regions(
            self,
            min_region_length: int = 5,
            zero_threshold: float = 0.002
            ):
        '''
        This method looks at the detected current regions and voltage profile
        to determine where the capacitor can be considered to be charging or
        discharging.
        Charging is defined as when the voltage is moving away from zero.
        In this case if current is positive, then if voltage is positive then 
        it is considered charging.

        :param min_region_length: Minimum length of a region to be considered
            valid. If a region is shorter than this, it will not be included in
            the detected regions.
        :param zero_threshold: Threshold for defining a region as a switch. If
            the voltage is between -zero_threshold and zero_threshold, then
            it is treated as zero in terms of defining the parity.
        '''
        self.detected_charging_regions_cache = []
        n = len(self.t) - 1

        # Function which saves a region if it is determined a valid region.
        def save_region_if_valid(
                current_parity: str,
                charging_parity: str,
                region_start,
                region_end
                ):
            # Don't save if zero voltage region
            if charging_parity == 'ZERO_VOLTAGE': return
            # Don't save if region is too short
            if (region_end - region_start + 1) >= min_region_length:
                if region_end == n:
                    region_end = -1
                self.detected_charging_regions_cache.append(
                    (current_parity, charging_parity, region_start, region_end)
                )

        # Function to determine the parity of value based on the zero threshold
        def voltage_parity(voltage: float) -> str:
            if voltage >= zero_threshold:
                return 'POSITIVE_VOLTAGE'
            elif voltage <= -zero_threshold:
                return 'NEGATIVE_VOLTAGE'
            else:
                return 'ZERO_VOLTAGE'
            
        # Function to determine the charging parity based on current and voltage
        def voltage_to_charging_parity(
                voltage_parity: str,
                current_parity: str
                ) -> str:
            if current_parity == 'POSITIVE_CURRENT':
                if   voltage_parity == 'POSITIVE_VOLTAGE': return 'CHARGING'
                elif voltage_parity == 'NEGATIVE_VOLTAGE': return 'DISCHARGING'
                elif voltage_parity == 'ZERO_VOLTAGE':     return 'ZERO_VOLTAGE'

            elif current_parity == 'NEGATIVE_CURRENT':
                if voltage_parity   == 'POSITIVE_VOLTAGE': return 'DISCHARGING'
                elif voltage_parity == 'NEGATIVE_VOLTAGE': return 'CHARGING'
                elif voltage_parity == 'ZERO_VOLTAGE':     return 'ZERO_VOLTAGE'

            elif current_parity == 'ZERO_CURRENT':         return 'ZERO_CURRENT'

        # Function to determine whether in a voltage hold or not
        def in_voltage_hold(index) -> bool:
            for hold in self.detected_voltage_hold_regions:
                hold_value, start_index, end_index = hold
                if end_index == -1: end_index = n
                if start_index <= index <= end_index: return True
            return False

        # Loop through all of the detected current regions
        for region in self.detected_current_regions:
                current_parity, start_index, end_index = region
                # If current is zero, then we skip this current region
                if current_parity == 'ZERO_CURRENT': continue
                if end_index == -1: end_index = n

                # If current is positive then we are charging initially
                E_parity = voltage_parity(self.E[start_index])
                sub_region_start = start_index
                sub_region_end   = start_index

                for i in range(start_index+1, end_index + 1):
                    new_voltage_parity = voltage_parity(self.E[i])
                    if new_voltage_parity != E_parity or in_voltage_hold(i):
                        # Calculate the charging parity
                        charging_parity = voltage_to_charging_parity(
                            E_parity, current_parity
                        )
                        # Save the region if valid
                        save_region_if_valid(
                            current_parity, charging_parity,
                            sub_region_start, sub_region_end
                        )
                        # Update the sub-region start and end
                        sub_region_start = i
                        sub_region_end = i
                        E_parity = new_voltage_parity
                    else:
                        sub_region_end = i
                
                # Save the last sub-region if valid
                charging_parity = voltage_to_charging_parity(
                    E_parity, current_parity
                )
                save_region_if_valid(
                    current_parity, charging_parity,
                    sub_region_start, sub_region_end
                )


    def detect_voltage_hold_regions(
            self,
            min_region_length: int = 25,
            zero_threshold: float = 0.001
            ):
        '''
        This method detects regions where the voltage is held constant.
        This is quite a common addition to GCD experiments and it is
        important to detect these in order to identify cycles correctly.

        :param min_region_length: Minimum length of a region to be considered
            valid. If a region is shorter than this, it will not be included in
            the detected regions.
        :param zero_threshold: Threshold for defining a region as a voltage hold.
            If the voltage change is less than this threshold, then it is
            considered a voltage hold region.
        '''
        self.detected_voltage_hold_regions_cache = []
        n = len(self.t) - 1

        def save_region_if_valid(hold_value, region_start, region_end):
            if (region_end - region_start + 1) >= min_region_length:
                if region_end == n:
                    region_end = -1
                self.detected_voltage_hold_regions_cache.append(
                    (hold_value, region_start, region_end)
                )

        E               = self.E
        hold_value      = E[0]
        region_start    = 0
        region_end      = 0
        for i, value in enumerate(E):
            if i == 0: continue
            if abs(value - hold_value) < zero_threshold:
                # Update the end of the region
                region_end = i

                # Update the hold value to be the average of the region so far
                hold_value = (hold_value * (region_end - region_start) + value) / \
                             (region_end - region_start + 1)
            else:
                save_region_if_valid(hold_value, region_start, region_end)
                hold_value    = value
                region_start  = i
                region_end    = i

        # Save the last region if valid
        save_region_if_valid(hold_value, region_start, region_end)


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
    

    def instantaneous_capacitances(self) -> List[np.ndarray]:
        '''
        Calaculates the instantaneous capacitance for each point in the 
        discharging sections of the GCD experiment.
        Q = CV, take the time derivative and assume that the capacitance is not
        a function of time, then dQ/dV = CdV/dt. 
        dQ/dV is of course the current, such that C = I / dV/dt.
        The voltage derivative is calculated as the average of the forward and
        backwards gradient.
        
        :return: List of numpy arrays, each corresponding to the instantaneous 
            capacitance for each discharging section of the GCD experiment.
        '''
        capacitances = []
        for section in self.detected_charge_discharge_cycles:
            charging, discharging = section
            d_i1, d_i2 = discharging[2], discharging[3]
            if d_i2 == -1:
                d_i2 = None
            # Calculate the voltage derivative
            dVdt = np.gradient(self.E[d_i1:d_i2], self.t[d_i1:d_i2])
            # Calculate the instantaneous capacitance
            C = self.I[d_i1:d_i2] / dVdt
            C /= 1000  # Convert from mA to A
            # Append to the list
            capacitances.append(C)
        return capacitances
        

            




        
