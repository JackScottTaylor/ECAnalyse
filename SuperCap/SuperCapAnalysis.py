# This module contains all of the fuctions which analyse data for supercapacitor experiments.
import numpy as np
from scipy.integrate import cumtrapz

def gradient_capacitances():
    # This function calculates the capacitance of the supercapacitor at each time point.
    # This is done using the gradient of the voltage-time curve.
    pass

def charging_data(file):
    # This function takes the file (ECLab normally) and returns antoehr instance of the file type
    # which only contains the data for the charging periods.
    # Charging is defined as when the current is positive.
    file.check_has_attributes('I')
    charging = file.in_data_range('I', 0, np.inf, closed_start=False)
    if len(charging.I) == 0: charging.start_time = file.start_time
    return charging

def discharging_data(file):
    # This function takes the file (ECLab normally) and returns antoehr instance of the file type
    # which only contains the data for the discharging periods.
    # Discharging is defined as when the current is negative.
    file.check_has_attributes('I')
    discharging = file.in_data_range('I', -np.inf, 0, closed_end=False)
    if len(discharging.I) == 0: discharging.start_time = file.start_time
    return discharging

def cumulative_charge(file):
    # Check that file has I and t attributes
    file.check_has_attributes('I', 't')
    # Calculate the cumulative charge in Coulombs
    return cumtrapz(file.I, file.t, initial=0) / 1000

def convert_C_to_mAh(charge):
    # This function converts charge in Coulombs to charge in mAh.
    # 1 C = 3600 mAh
    return charge * 1000 / 3600

def capacitance_using_voltage_difference(file):
    # This function calculates the capacitance at each time point
    # using C = Q/V where Q is the charge passed and in this case
    # V is the difference in voltage since the start of the experiment.
    file.check_has_attributes('I', 't', 'E')
    charge, voltage = np.array([]), np.array([])
    if file.I.size > 0:
        charge = cumulative_charge(file)
        voltage = file.E - file.E[0]
    return charge / voltage

def coulomb_efficiency_of_single_cycle(file):
    # The provided file should contain only a single cycle.
    # Coulomb efficiency defined as total charge passed during 
    # negative current divided by total charge passed during positive current.
    # Returns value as a percentage.
    file.check_has_attributes('I', 't')
    charging, discharging       = charging_data(file), discharging_data(file)
    charge_passed_charging      = 0
    charge_passed_discharging   = 0
    if charging.I.size > 0:
        charge_passed_charging = cumulative_charge(charging)[-1]
    if discharging.I.size > 0:
        charge_passed_discharging   = cumulative_charge(discharging)[-1]
    if charge_passed_discharging == 0: return 0
    return abs(100 * charge_passed_discharging / charge_passed_charging)

