# This module contains the functions used for making plots for SuperCap experiments.
from ..custom_plt import custom_plt
from ..plotting_funcs import full_labels_list, check_start_times_same_type, gen_params_list
from ..plotting_funcs import apply_plot_func_to_all_cycles_in_all_files
from ..plotting_funcs import apply_plot_func_to_all_files
from .SuperCapAnalysis import charging_data, discharging_data, cumulative_charge, convert_C_to_mAh, coulomb_efficiency_of_single_cycle
from .SuperCapAnalysis import capacitance_using_voltage_difference
import numpy as np
import itertools

plt = custom_plt()

def plot_GCD(*files, labels=[], use_params=False, ax=plt.gca()):
    # In GCD experiments, constant current is applied.
    # Voltage is plotted against time.

    # Make sure that labels list is full and that all files have the same start_time type.
    labels = full_labels_list(files, labels)
    check_start_times_same_type(files)
    # Generate the params_list
    params_list = gen_params_list(files, use_params)
    # Take the global start_time as the start_time fo the first file
    start_time = files[0].start_time

    def plot_one_file(file, label, params):
        ax.plot(file.elapsed_time(start_time), file.E, label=label, **params)

    # Apply plotting function to all files in the standard way.
    apply_plot_func_to_all_cycles_in_all_files(
        plot_one_file, files, labels, params_list,
        required_attributes = ['E', 't']
    )
    # Finally set the labels of the plot.
    ax.set_xlabel('Time / s')
    ax.set_ylabel('Voltage / V')
        
        
def plot_GCD_E_vs_Q(*files, labels=[], use_params=False, charge_unit='C', ax=plt.gca()):
    # In GCD experiments, constant current is applied.
    # voltage is plotted against charge.
    labels = full_labels_list(files, labels)
    check_start_times_same_type(files)
    params_list = gen_params_list(files, use_params)

    def plot_one_cycle(file, label, params):
        # Extract the charging and discharging data
        charging, discharging = charging_data(file), discharging_data(file)
        # Calculate the cumulative charge in Coulombs.
        # If charging or discharging empty then set charge to empty array.
        charging_charge, discharging_charge = np.array([]), np.array([])
        if charging.I.size > 0: charging_charge = abs(cumulative_charge(charging))
        if discharging.I.size > 0: discharging_charge = abs(cumulative_charge(discharging))
        # Convert charge to mAh if charge_unit is 'mAh'
        # Raise error if charge_unit is not 'C' or 'mAh'
        if charge_unit == 'mAh':
            charging_charge, discharging_charge = convert_C_to_mAh(charging_charge), convert_C_to_mAh(discharging_charge)
        elif charge_unit != 'C':
            raise ValueError('charge_unit must be either "C" or "mAh"')
        # Finally plot the two sets of data with the correct params.
        ax.plot(charging_charge, charging.E, label=label, **params)
        ax.plot(discharging_charge, discharging.E, **params)

    apply_plot_func_to_all_cycles_in_all_files(
        plot_one_cycle, files, labels, params_list,
        required_attributes = ['E', 't']
    )

    # Finally set the labels and limits of the plot.
    ax.set_xlabel(f'Capacity / {charge_unit}')
    ax.set_ylabel('Voltage / V')
    ax.set_xlim(left=0)


def plot_GCD_C_vs_E(*files, labels=[], use_params=False, ax=plt.gca()):
    # The Capacitance C=Q/V is plotted against voltage.
    labels = full_labels_list(files, labels)
    check_start_times_same_type(files)
    params_list = gen_params_list(files, use_params)

    def make_plot(file, label, params):
        # First extract the charging and discharging data.
        charging, discharging = charging_data(file), discharging_data(file)
        # Calculate the capacitance using the voltage difference.
        charging_capacitance    = capacitance_using_voltage_difference(charging)
        discharging_capacitance = capacitance_using_voltage_difference(discharging)
        # Finally plot the data.
        ax.plot(charging.E, charging_capacitance, label=label, **params)
        ax.plot(discharging.E, discharging_capacitance, **params)

    apply_plot_func_to_all_cycles_in_all_files(
        make_plot, files, labels, params_list,
        required_attributes = ['E', 't', 'I']
    )
    # Finally set the labels of the plot.
    ax.set_xlabel('Voltage / V')
    ax.set_ylabel('Capacitance / F')


def plot_GCD_specific_C_vs_E(mass1, *files, mass2=None, labels=[], use_params=False, ax=plt.gca()):
    # Similar to plot_GCD_C_vs_E but uses specific capacitance instead.
    # If only one mass provided then the same mass is used for both.
    if mass2 == None: mass2 = mass1
    mean_mass = (mass1 + mass2) / 2

    labels      = full_labels_list( files, labels)
    params_list = gen_params_list(  files, use_params)
    check_start_times_same_type(files)

    def make_plot(file, label, params):
        # First extract the charging and discharging data.
        charging, discharging = charging_data(file), discharging_data(file)
        # Calculate the capacitance using the voltage difference.
        charging_capacitance    = capacitance_using_voltage_difference(charging)
        discharging_capacitance = capacitance_using_voltage_difference(discharging)

        charging_capacitance    = 2 * charging_capacitance / mean_mass
        discharging_capacitance = 2 * discharging_capacitance / mean_mass

        ax.plot(charging.E, charging_capacitance, label=label, **params)
        ax.plot(discharging.E, discharging_capacitance, **params)

    apply_plot_func_to_all_cycles_in_all_files(
        make_plot, files, labels, params_list,
        required_attributes = ['E', 't', 'I']
    )
    # Finally set the labels of the plot.
    ax.set_xlabel('Voltage / V')
    ax.set_ylabel('Specific Capacitance / F/g')


def plot_GCD_Coulomb_efficiencies(*files, labels=[], use_params=False, ax=plt.gca()):
    # This function plots the coulomb efficiencies of each cycle in the file.
    labels = full_labels_list(files, labels)
    params = gen_params_list(files, use_params)
    check_start_times_same_type(files)

    def plot_efficiency_vs_cycle_number(file, label, params):
        efficiencies = []
        for cycle in np.unique(file.c):
            cycle_file = file.cycle(cycle)
            efficiency = coulomb_efficiency_of_single_cycle(cycle_file)
            efficiencies.append(efficiency)
        ax.plot(np.unique(file.c), efficiencies, label=label, **params)

    apply_plot_func_to_all_files(
        plot_efficiency_vs_cycle_number, files, labels, params,
        required_attributes = ['I', 't']
    )

    ax.set_xlabel('Cycle Number')
    ax.set_ylabel('Coulombic Efficiency / %')





