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




## `plot_one_cycle`




# `plot_GCD_C_vs_E`




## `make_plot`




# `plot_GCD_specific_C_vs_E`




## `make_plot`




# `plot_GCD_Coulomb_efficiencies`




## `plot_efficiency_vs_cycle_number`




