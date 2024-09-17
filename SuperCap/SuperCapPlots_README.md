This module contains the functions for generating plots from supercapacitor experiments.

Data is most often analysed using the functions in SuperCapAnalysis


# Table of Contents

- [`plot_GCD`](#`plot_gcd`)
  - [`plot_one_file`](#`plot_one_file`)
- [`plot_GCD_E_vs_Q`](#`plot_gcd_e_vs_q`)
  - [`plot_one_cycle`](#`plot_one_cycle`)
- [`plot_GCD_C_vs_E`](#`plot_gcd_c_vs_e`)
  - [`make_plot`](#`make_plot`)
- [`plot_GCD_specific_C_vs_E`](#`plot_gcd_specific_c_vs_e`)
  - [`make_plot`](#`make_plot`)
- [`plot_GCD_Coulomb_efficiencies`](#`plot_gcd_coulomb_efficiencies`)
  - [`plot_efficiency_vs_cycle_number`](#`plot_efficiency_vs_cycle_number`)

# `plot_GCD`

**Description:**

This function plots the voltage against time, which is the standard plot for GCD experiments.

X and Y axes are labelled correctly.



**Arguments:**

- *files: Data (usually ECLab_File)

The data files to be plotted.

- labels = []: list

The labels to be used for the legend. Default is empty list which means no entries added to legend.

- use_params = False: bool

If True, then the style each file is plotted with is determined by the file's plot_params attribute. Default is to use the default plot style.

- ax = plt.gca(): matplotlib.pyplot.Axes

The axes object to plot the data on. Default is the current axis.



**Examples:**

```python
GCD = ECLab_File('/Users/jack/Documents/GitHub/ECAnalyse/tests/data_files/ACC-20, 1M Na2SO4, N2 10mlmin-1, CO2 2,5mlmin-1, 2,5rpm_C01.txt')
GCD_0123 = GCD.cycles(0,1,2,3)
GCD_6789 = GCD.cycles(6,7,8,9)
GCD_111213   = GCD.cycles(11,12,13)
plot_GCD(GCD_0123, GCD_6789, GCD_111213, labels=['0,1,2,3', '6,7,8,9', '11,12,13'])
plt.title('Example of a GCD plot')
plt.legend()
plt.show()
```

![Example of plot_GCD figure](/SuperCap/ReadMeImages/plot_GCD.png)


## `plot_one_file`

**Description:**

This function is internal to plot_GCD and plots the voltage against time for a single file.


# `plot_GCD_E_vs_Q`

**Description:**

For a GCD experiment, voltage is generally scanned between two limits.

This function plots the voltage against the charge passed in Coulomns.

Each time the scan direction changes, the charge is reset to zero.



**Arguments:**

- *files: Data (usually ECLab_File)

The data files to be plotted.

- labels = []: list

The labels to be used for the legend. Default is empty list which means no entries added to legend.

- use_params = False: bool

If True, then the style each file is plotted with is determined by the file's plot_params attribute. Default is to use the default plot style.

- charge_unit = 'C': str

The units of charge to be plotted. Default is Coulombs. Other option in 'mAh'.

- ax = plt.gca(): matplotlib.pyplot.Axes

The axes object to plot the data on. Default is the current axis.



**Examples:**

```python
from ECAnalyse.SuperCap.SuperCapPlots import *
from ECAnalyse.File_Types import ECLab_File
from ECAnalyse.custom_plt.color_palettes import IBM
GCD = ECLab_File('/Users/jack/Documents/GitHub/ECAnalyse/tests/data_files/ACC-20, 1M Na2SO4, N2 10mlmin-1, CO2 2,5mlmin-1, 2,5rpm_C01.txt')
GCD_0123 = GCD.cycles(0,1,2,3)
GCD_6789 = GCD.cycles(6,7,8,9)
GCD_1112  = GCD.cycles(11,12)
GCD_0123.plot_params = {'color': IBM[0], 'linestyle': '-'}
GCD_6789.plot_params = {'color': IBM[1], 'linestyle': '--'}
GCD_1112.plot_params = {'color': IBM[2], 'linestyle': ':'}
plot_GCD_E_vs_Q(GCD_0123, GCD_6789, GCD_1112, labels=['0,1,2,3', '6,7,8,9', '11,12'], use_params=True)
plt.title('Example of a Voltage vs Charge plot')
plt.legend()
plt.show()
```



![Example of plot_GCD_E_vs_Q figure](/SuperCap/ReadMeImages/plot_GCD_E_vs_Q.png)


## `plot_one_cycle`

**Description:**

Internal function to plot_GCD_E_vs_Q


# `plot_GCD_C_vs_E`

**Description:**

This function uses `capacitance_using_voltage_difference` to calculate the capacitance at each voltage

and then plots this calculated capacitance against the measured voltage.



**Arguments:**

- *files: Data (usually ECLab_File)

The data files to be plotted.

- labels = []: list

The labels to be used for the legend. Default is empty list which means no entries added to legend.

- use_params = False: bool

If True, then the style each file is plotted with is determined by the file's plot_params attribute. Default is to use the default plot style.

- ax = plt.gca(): matplotlib.pyplot.Axes

The axes object to plot the data on. Default is the current axis.



**Examples:**

```python
from ECAnalyse.auto_readme import auto_readme
from ECAnalyse.SuperCap.SuperCapPlots import *
from ECAnalyse.File_Types import ECLab_File
from ECAnalyse.custom_plt.color_palettes import IBM
GCD = ECLab_File('/Users/jack/Documents/GitHub/ECAnalyse/tests/data_files/ACC-20, 1M Na2SO4, N2 10mlmin-1, CO2 2,5mlmin-1, 2,5rpm_C01.txt')
GCD_123 = GCD.cycles(1,2,3)
GCD_6789 = GCD.cycles(6,7,8,9)
GCD_1112  = GCD.cycles(11,12)
GCD_123.plot_params = {'color': IBM[0], 'linestyle': '-'}
GCD_6789.plot_params = {'color': IBM[1], 'linestyle': '--'}
GCD_1112.plot_params = {'color': IBM[2], 'linestyle': ':'}
plot_GCD_C_vs_E(GCD_123, GCD_6789, GCD_1112, labels=['0,1,2,3', '6,7,8,9', '11,12'], use_params=True)
plt.title('Example of a Capacitance vs Voltage Plot')
plt.legend()
plt.show()
```

![Example of plot_GCD_C_vs_E figure](/SuperCap/ReadMeImages/plot_GCD_C_vs_E.png)


## `make_plot`

**Description:**

Internal function to plot_GCD_C_vs_E


# `plot_GCD_specific_C_vs_E`

**Description:**

This function calculates the specific capacitance by dividing the capacitance by the mean mass. The capacitance is also multiplied by two to account for the two double layers.



**Arguments:**

- mass1: float

The mass of the first electrode in grams.

- *files: Data (usually ECLab_File)

The data files to be plotted.

- mass2 = None: float

The mass of the second electrode in grams. If None then the same mass is used for both.

- labels = []: list

The labels to be used for the legend. Default is empty list which means no entries added to legend.

- use_params = False: bool

If True, then the style each file is plotted with is determined by the file's plot_params attribute. Default is to use the default plot style.

- ax = plt.gca(): matplotlib.pyplot.Axes

The axes object to plot the data on. Default is the current axis.


## `make_plot`




# `plot_GCD_Coulomb_efficiencies`




## `plot_efficiency_vs_cycle_number`




