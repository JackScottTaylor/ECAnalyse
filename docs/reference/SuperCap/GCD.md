# GCD Class Documentation

## Overview
The `GCD` class is designed for handling and analyzing Galvanostatic Charge-Discharge (GCD) data. It inherits from `ECLab_File` and expects the input data file to contain **time**, **current**, and **voltage** data. If any of these are missing, an error will be raised.

This class provides methods and properties to detect and analyze important regions and cycles within the GCD data, such as current regions, charging/discharging phases, voltage hold regions, and charge-discharge cycles.

---

## Properties

### mass1
- **Type**: float
- **Description**: Mass of the first electrode in mg.

### mass2
- **Type**: float
- **Description**: Mass of the second electrode in mg.

### detected_current_regions
- **Type**: List[tuple]
- **Description**: Returns the detected current regions in the form of a list of tuples where each tuple is formatted as (positive/negative/zero, start_index, end_index).

### detected_charging_regions
- **Type**: List[tuple]
- **Description**: Returns the detected charging regions in the form of a list of tuples where each tuple has format: (current_region, charging_profile, start_index, end_index).

### detected_charge_discharge_cycles
- **Type**: List[tuple]
- **Description**: Returns the detected charge-discharge cycles in the form of a list of tuples where each tuple has format: (charging_region, discharging_region).

## Initialisation

### __init__(self, filepath: Optional[str] = None, mass1: float = 0.0, mass2: float = 0.0)
- **Description**: Initializes the GCD object with the given file path and electrode masses in mg.

## Region Detection Methods

### detect_current_regions(self, zero_threshold: float = 0.1, min_region_length: int = 5)
- **Description**:
This method detects regions of the GCD data where the current is either
positive, negative, or zero. Zero current is defined as being between 
±zero_threshold and zero_threshold. A region must also contain at least
min_region_length data points to be considered a valid region. Detected
regions are accessed via the `detected_regions` property. They are
stored as a list of tuples in the format: 
(region_type, start_index, end_index) where region_type is one of
'POSITVE_CURRENT', 'NEGATIVE_CURRENT', or 'ZERO_CURRENT'.
The start_index and end_index are the indices of the first and last data
points in the region, respectively.
If end_index corresponds to last data point, then it is saved as -1.

### detect_charging_regions(self, min_region_length: int = 5, zero_threshold: float = 0.002)
- **Description**:
This method looks at the detected current regions and voltage profile
to determine where the capacitor can be considered to be charging or
discharging.
Charging is defined as when the voltage is moving away from zero.
In this case if current is positive, then if voltage is positive then 
it is considered charging.

### detect_voltage_hold_regions(self, min_region_length: int = 25, zero_threshold: float = 0.001)
- **Description**:
This method detects regions where the voltage is held constant.
This is quite a common addition to GCD experiments and it is
important to detect these in order to identify cycles correctly.

### detect_charge_discharge_cycles(self)
- **Description**
This requires that the switch regions have already been detected.
        A charge-discharge cycle is a charging region followed by a discharging
        region, possibly with a zero region inbetween.

### charge_discharge_cycle_times(self)
- **Description**
Calculates the charge-discharge cycle times using the detected 
        charge-discharge cycles. The cycle time is defined as the time between
        the start of the charging region and the end of the discharging region.

## Analysis Methods
### Coulomb_efficiencies(self) -> np.ndarray
Calculates the charge-discharge cycle Coulomb efficiencies using the 
        detected charge-discharge cycles. The Coulomb efficiency is defined as
        discharged charge / charging charge, as a percentage.

### energy_efficiencies(self) -> np.ndarray
Calculates the charge-discharge cycle energy efficiencies using the 
        detected charge-discharge cycles. The energy efficiency is defined as
        discharged energy / charging energy, as a percentage.

### resistances(self) -> np.ndarray
Calculates the resistance for each charge-discharge cycle using the 
        ohmic drop method. R = ΔV / ΔI, where ΔV is the voltage drop and 
        ΔI is the change in current. Voltage drop calculated as difference
        last voltage in charge region and first voltage in discharge region.
        ΔI is the change in current between the same two points.

### instantaneous_capacitances(self, window: int = 10) -> List[np.ndarray]
Calaculates the instantaneous capacitance for each point in the 
        discharging sections of the GCD experiment.
        Q = CV, take the time derivative and assume that the capacitance is not
        a function of time, then dQ/dV = CdV/dt. 
        dQ/dV is of course the current, such that C = I / dV/dt.
        The derivative is calculated using linear regression over a sliding
        window of size window. The current is taken as the average current over
        the same window.
        Capacitance here is calculated in Farads
        
        :param window: The window size over which linear regression is applied.
        :return: List of numpy arrays, each corresponding to the instantaneous 
            capacitance for each discharging section of the GCD experiment.

### gravimetric_instantaneous_capacitances(self, window: int = 10) -> List[np.ndarray]
This method calculates the gravimetric instantaneous capacitance for 
        each discharging section of the GCD experiment.
        The convention used here is that the supercap consists of two double-
        layer capacitors in series. The two in-series capacitors are assumed to 
        be equal, such that the total capacitance is given by: 
        C_total = C_single / 2. The gravimetrric capacitance is then obtained 
        by dividing the single-electrode capacitance by half the total mass.

        :param window: The window size over which linear regression is applied 
            to calculate the instantaneous capacitance.
        :return: List of numpy arrays, each corresponding to the gravimetric 
            instantaneous capacitance for each discharging section of the GCD
            experiment. 

### cycle_capacitances_instantaneous_average(self, window: int = 10, over_last: float = 0.25) -> np.ndarray
This method calculates the capacitance for each charge-discharge cycle
        by taking the average of the instantaneous capacitance over the last
        over_last portion of the discharge step.

        :param window: The window size over which linear regression is applied 
            to calculate the instantaneous capacitance.
        :param over_last: The portion of the discharge step to average over,
            expressed as a fraction of the total discharge step length.
            For example, 0.25 means the last 25% of the discharge step.
        :return: Numpy array of average capacitances for each charge-discharge
            cycle, calculated as the average of the instantaneous capacitance
            over the last over_last portion of the discharge step.

### cycle_capacitances_linear_regression(self, over_last: float = 0.25) -> np.ndarray
This method calculates the capacitance for each charge-discharge cycle
        by performing linear regression on the voltage profile over the last
        over_last portion of the discharge step. The capacitance is calculated
        as the slope of the linear fit to the voltage profile.

        :param over_last: The portion of the discharge step to average over,
            expressed as a fraction of the total discharge step length.
            For example, 0.25 means the last 25% of the discharge step.
        :return: Numpy array of average capacitances for each charge-discharge
            cycle, calculated as the slope of the linear fit to the voltage
            profile over the last over_last portion of the discharge step.

### cycle_capacitances(self, linear_regression: bool = False, window: int = 10, over_last: float = 0.25) -> np.ndarray
This method calculates the capacitance for each charge-discharge cycle.
        It can either use the instantaneous capacitance method or the linear
        regression method to calculate the capacitance.

        :param linear_regression: If True, use linear regression to calculate
            capacitance. If False, use average over instantaneous capacitance.
        :param window: The window size for calculating instantaneous capacitance
        :param over_last: The portion of the discharge step to average over,
            expressed as a fraction of the total discharge step length.
            For example, 0.25 means the last 25% of the discharge step.
        :return: Numpy array of capacitances for each charge-discharge cycle.

### gravimetric_cycle_capacitances(self, linear_regression: bool = False, window: int = 10, over_last: float = 0.25) -> np.ndarray
This method calculates the gravimetric capacitance for each 
        charge-discharge cycle. It can either use the instantaneous capacitance
        method or the linear regression method to calculate the capacitance.

        :param linear_regression: If True, use linear regression to calculate
            capacitance. If False, use average over instantaneous capacitance.
        :param window: The window size for calculating instantaneous capacitance
        :param over_last: The portion of the discharge step to average over,
            expressed as a fraction of the total discharge step length.
            For example, 0.25 means the last 25% of the discharge step.
        :return: Numpy array of gravimetric capacitances for each 
            charge-discharge cycle.

## Plotting Methods

### plot(self,ax: Optional[Axes] = None, title: str = '', rolling_average: bool = False, window_size: int = 10, **kwargs) -> Axes
Plots the GCD experiment data as Voltage vs Time

        :param ax: matplotlib Axes object to plot on. If None then uses current
            active Axes.
        :param title: Title for the plot
        :param rolling_average: If True, applies a rolling average to the data
        :param window_size: Size of the rolling average window if using
        :param kwargs: Additional keyword arguments to pass to the plot

### plot_current(self, ax: Optional[Axes] = None, labels: Optional[List[str]] = None, title: str = '', rolling_average: bool = False, window_size: int = 10, **kwargs) -> Axes
Plots the GCD experiment data as Current vs Time

        :param ax: matplotlib Axes object to plot on. If None then uses current
            active Axes.
        :param title: Title for the plot
        :param rolling_average: If True, applies a rolling average to the data
        :param window_size: Size of the rolling average window if using
        :param kwargs: Additional keyword arguments to pass to the plot

### plot_charging_regions(self, ax: Optional[Axes] = None, **kwargs ) -> Axes
Plots the voltage profile against time, however colours the regions it
        has detected as either charging, discharging or zero in different 
        colours.

        :param ax: matplotlib Axes object to plot on. If None then uses current
            active Axes.
        :param kwargs: Additional keyword arguments to pass to the plot

### plot_charge_discharge_cycles(self, ax: Optional[Axes] = None, **kwargs) -> Axes
Plots the charge-discharge cycles detected in the GCD experiment.

        :param ax: matplotlib Axes object to plot on. If None then uses current
            active Axes.
        :param kwargs: Additional keyword arguments to pass to the plot

### full_analysis(self)
This method performs all of the necessary analysis on the GCD experiment
        and saves the results as pdf files in the specified directory. It also
        saves the calculated results in a text file in the same directory.