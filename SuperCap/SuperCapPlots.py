# This module contains the functions used for making plots for SuperCap experiments.
from ..custom_plt import custom_plt
from ..plotting_funcs import full_labels_list, check_start_times_same_type
from .SuperCapAnalysis import charging_data, discharging_data, cumulative_charge, convert_C_to_mAh
import numpy as np
from scipy.integrate import cumtrapz
plt = custom_plt()

def plot_GCD(*files, labels=[], use_params=False, ax=plt.gca()):
    # In GCD experiments, constant current is applied.
    # Voltage is plotted against time.
    # First fill labels with None until same size as files
    labels = full_labels_list(files, labels)
    check_start_times_same_type(files)

    # Each file must be calibrated so that times are correct
    # Take the global start_time as the start_time fo the first file
    start_time = files[0].start_time

    for file, label in zip(files, labels):
        # Check that the object has both E and t attribues:
        file.check_has_attributes('E', 't')
        if use_params: ax.plot(file.elapsed_time(start_time), file.E, label=label, **file.plot_params)
        else: ax.plot(file.elapsed_time(start_time), file.E, label=label)

    ax.set_xlabel('Time / s')
    ax.set_ylabel('Voltage / V')
        
        
def plot_GCD_E_vs_Q(*files, labels=[], use_params=False, charge_unit='C', ax=plt.gca()):
    # In GCD experiments, constant current is applied.
    # voltage is plotted against charge.
    labels = full_labels_list(files, labels)
    check_start_times_same_type(files)

    def make_plot(file, plot_params, label):
        charging, discharging = charging_data(file), discharging_data(file)
        if charging.I.size > 0: charging_charge = abs(cumulative_charge(charging))
        else: charging_charge = np.array([])
        if discharging.I.size > 0: discharging_charge = abs(cumulative_charge(discharging))
        else: discharging_charge = np.array([])
        if charge_unit == 'mAh':
            charging_charge, discharging_charge = convert_C_to_mAh(charging_charge), convert_C_to_mAh(discharging_charge)
        elif charge_unit != 'C':
            raise ValueError('charge_unit must be either "C" or "mAh"')
        if use_params:
            print('Use_params = True')
            ax.plot(charging_charge, charging.E, label=label, **plot_params)
            ax.plot(discharging_charge, discharging.E, **plot_params)
        else:
            ax.plot(charging_charge, charging.E, label=label)
            ax.plot(discharging_charge, discharging.E)

    for file, label in zip(files, labels):
        # Check that object has, E, t, and I attributes.
        file.check_has_attributes('E', 't', 'I')
        # If file has cycle number attribute then iterate through each cycle,
        # otherwise plot all together.
        if hasattr(file, 'c'):
            for cycle in np.unique(file.c):
                file_cycle = file.cycle(cycle)
                make_plot(file_cycle, file.plot_params, label)
        
        else: make_plot(file, file.plot_params, label)

    ax.set_xlabel(f'Capacity / {charge_unit}')
    ax.set_ylabel('Voltage / V')
    ax.set_xlim(left=0)


def plot_GCD_C_vs_E(*files, labels=[], use_params=False, ax=plt.gca()):
    # The Capacitance C=Q/V is plotted against voltage.
    labels = full_labels_list(files, labels)
    check_start_times_same_type(files)

    def make_plot(file, plot_params, label):
        charging, discharging = charging_data(file), discharging_data(file)
        if charging.I.size > 0:
            charging_charge = abs(cumulative_charge(charging))
            charging_voltage = charging.E - charging.E[0]
        else: charging_charge, charging_voltage = np.array([]), np.array([])
        if discharging.I.size > 0: 
            discharging_charge = abs(cumulative_charge(discharging))
            discharging_voltage = discharging.E[0] - discharging.E
        else: discharging_charge, discharging_voltage = np.array([]), np.array([])
        charging_capacitance = charging_charge / charging_voltage
        discharging_capacitance = discharging_charge / discharging_voltage
        if use_params:
            ax.plot(charging.E, charging_capacitance, label=label, **plot_params)
            ax.plot(discharging.E, discharging_capacitance, **plot_params)
        else:
            ax.plot(charging.E, charging_capacitance, label=label)
            ax.plot(discharging.E, discharging_capacitance)

    for file, label in zip(files, labels):
        file.check_has_attributes('E', 't', 'I')
        if hasattr(file, 'c'):
            for cycle in np.unique(file.c):
                file_cycle = file.cycle(cycle)
                make_plot(file_cycle, file.plot_params, label)
        else: make_plot(file, file.plot_params, label)

    ax.set_xlabel('Voltage / V')
    ax.set_ylabel('Capacitance / F')


def plot_GCD_specific_C_vs_E(mass1, *files, mass2=None, labels=[], use_params=False, ax=plt.gca()):
    # Similar to plot_GCD_C_vs_E but uses specific capacitance instead.
    if mass2 == None: mass2 = mass1
    mean_mass = (mass1 + mass2) / 2
    labels = full_labels_list(files, labels)
    check_start_times_same_type(files)

    def make_plot(file, plot_params, label):
        charging, discharging = charging_data(file), discharging_data(file)
        if charging.I.size > 0:
            charging_charge = abs(cumulative_charge(charging))
            charging_voltage = charging.E - charging.E[0]
        else: charging_charge, charging_voltage = np.array([]), np.array([])
        if discharging.I.size > 0: 
            discharging_charge = abs(cumulative_charge(discharging))
            discharging_voltage = discharging.E[0] - discharging.E
        else: discharging_charge, discharging_voltage = np.array([]), np.array([])
        charging_capacitance = 2 * charging_charge / charging_voltage / mean_mass
        discharging_capacitance = 2 * discharging_charge / discharging_voltage / mean_mass
        if use_params:
            ax.plot(charging.E, charging_capacitance, label=label, **plot_params)
            ax.plot(discharging.E, discharging_capacitance, **plot_params)
        else:
            ax.plot(charging.E, charging_capacitance, label=label)
            ax.plot(discharging.E, discharging_capacitance)

    for file, label in zip(files, labels):
        file.check_has_attributes('E', 't', 'I')
        if hasattr(file, 'c'):
            for cycle in np.unique(file.c):
                file_cycle = file.cycle(cycle)
                make_plot(file_cycle, file.plot_params, label)
        else: make_plot(file, file.plot_params, label)

    ax.set_xlabel('Voltage / V')
    ax.set_ylabel('Specific Capacitance / F/g')






