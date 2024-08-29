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