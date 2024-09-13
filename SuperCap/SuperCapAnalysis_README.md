This module contains functions used for the analysis of supercapacitor data.


# Table of Contents

- [`charging_data`](#`charging_data`)
- [`discharging_data`](#`discharging_data`)
- [`cumulative_charge`](#`cumulative_charge`)
- [`convert_C_to_mAh`](#`convert_c_to_mah`)
- [`capacitance_using_voltage_difference`](#`capacitance_using_voltage_difference`)
- [`coulomb_efficiency_of_single_cycle`](#`coulomb_efficiency_of_single_cycle`)

# `charging_data`

**Description:**

This function takes a Data object (usually an ECLab_File) and returns a new Data object which only contains the data for the charging periods.

Charging is defined as when current is greater than zero.



**Arguments:**

- file: Data (usually ECLab_File)

The data file from which the charging data is to be extracted.



**Returns:**

- Data (same type as file)

A new Data object which only contains the charging data.


# `discharging_data`

**Description:**

This function takes a Data object (usually an ECLab_File) and returns a new Data object which only contains the data for the discharging periods.

Discharging is defined as when current is less than zero.



**Arguments:**

- file: Data (usually ECLab_File)

The data file from which the discharging data is to be extracted.



**Returns:**

- Data (same type as file)

A new Data object which only contains the discharging data.


# `cumulative_charge`

**Description:**

This function calculates at each time point the cumulative charge passed since the start of the experiment. The charge is in Coulombs.



**Arguments:**

- file: Data (usually ECLab_File)

The data file from which the charge is to be calculated.



**Returns:**

- np.ndarray

An array containing the cumulative charge passed at each time point.



**Methodology:**

- The charge is calculated by integrating the current with respect to time.

$$ Q(t) = \int_{0}^{t} I(t) dt $$

- Integration performed using trapezoidal rule.


# `convert_C_to_mAh`

**Description:**

This function converts charge in Coulombs to charge in mAh.



**Arguments:**

- charge: float

The charge in Coulombs to be converted.



**Returns:**

- float

The charge in mAh.



**Methodology:**

- Divides the charge by 3.6


# `capacitance_using_voltage_difference`

**Description:**

This function calculates the capacitance of the supercapacitor at each time point.

Capacitance is calculated in Farads.



**Arguments:**

- file: Data (usually ECLab_File)

The data file from which the capacitance is to be calculated.



**Returns:**

- np.ndarray

An array containing the capacitance in Farads at each time point.



**Methodology:**

- The capacitance is calculated using the formula:

$$ C = \frac{\Delta Q}{\Delta V} $$

- $C$ is the capacitance in Farads,

- $\Delta Q$ is the charge passed in Coulombs, since the start of the file, found using `cumulative_charge` function,

- $\Delta V$ is the voltage difference since the start of the experiment.



**Note:**

- The first $\Delta V$ value is always zero.

- When numpy divides by zero, it returns `nan` values.

- Therefore the first value of the capacitance array is also `nan`.



**Examples:**

```python

file = ECLab_File('data.txt')

charging_section_cycle1 = charging_data(file.cycle(1))

""" Best to do this calculation for individual cycles and charging directions. """

capacitance = capacitance_using_voltage_difference(charging_section_cycle1)

```


# `coulomb_efficiency_of_single_cycle`

**Description:**

This function calculates the Colomb efficiency of a single cycle, where a single cycle refers to an electrochemical experiment where there is a distinct charging and discharging period, this is usually used for GCD experiments.

Coulomb efficiency is defined as the total charge passed during the discharging period divided by the total charge passed during the charging period.

The value is returned as a percentage.



**Arguments:**

- file: Data (usually ECLab_File)

The data file containing a single cycle of charging and discharging data.



**Returns:**

- float

The Coulomb efficiency as a percentage.



**Methodology:**

- The charge passed during charging and discharging periods is calculated using `cumulative_charge`.

- The Coulomb efficiency is then calculated as:

$$ \text{Coulomb efficiency} = \frac{\text{charge passed during discharging}}{\text{charge passed during charging}} \times 100 $$


