# This module contains some functions that plot functions
# may commonly wish to use.

from ..custom_plt import custom_plt
plt = custom_plt()

import itertools
import numpy as np

def full_labels_list(files, labels):
    # This function fills the labels list with None until
    # it is the same length as the files list.
    while len(labels) < len(files):
        labels.append(None)
    return labels

def check_start_times_same_type(files):
    # This function checks that all the start_times are either
    # datetime, or they are equal to 0
    # If they are not then an error is raised.
    first_file_type = type(files[0].start_time)
    for file in files:
        if type(file.start_time) != first_file_type:
            raise ValueError(
                'All files must have the same type of start_time.'
            )
        if type(file.start_time) == int:
            if file.start_time != 0:
                raise ValueError(
                    'For files with only elapsed time, start_time should equal 0'
                )
            
def gen_params_list(files, use_params):
    # If use_params is False then this returns a list of 
    # dictionaries corresponding to the default plot cycler.
    # This is necessary as some plotting functions plot by cycle
    # but one would want cycles from the same file to be plotted in the same
    # style. If use_params is true the the parameters are simply those stored in 
    # the file.plot_params attribute.
    if not use_params:
        cycler_iterator = itertools.cycle(plt.rcParams['axes.prop_cycle'])
        return [next(cycler_iterator) for file in files]
    else: return [file.plot_params for file in files]


def apply_plot_func_to_all_cycles_in_all_files(
        plot_function, files, labels, params_list,
        required_attributes = []):
    # This function is used when a plotting function needs to plot by cycle,
    # but all cycles in the same file need to be plotted in the same style.
    # It also ensures that each file is only added to the legend once.
    for file, label, params in zip(files, labels, params_list):
        # Check that the file has the required attributes
        file.check_has_attributes(*required_attributes)
        # If the file has a cycle attribute then iterate through each cycle
        # otherwise plot the whole file.
        labels = [label]
        # If the file has a cycle attribute then extract the data from each file
        # and store in list of files to plot.
        if hasattr(file, 'c'):
            cycles = np.unique(file.c)
            files_to_plot = [file.cycle(c) for c in cycles]
            # Each file should only appear in legend once so if there are multiple
            # cycles then the label should be None for all but the first cycle
            if len(cycles) > 1: labels = full_labels_list(files_to_plot, [label])
        else: files_to_plot = [file]

        for file_to_plot, label in zip(files_to_plot, labels):
            plot_function(file_to_plot, label, params)

def apply_plot_func_to_all_files(
        plot_function, files, labels, params_list,
        required_attributes = []):
    # This function is used when a plotting function needs to plot by file.
    for file, label, params in zip(files, labels, params_list):  
        # Check that the file has the required attributes
        file.check_has_attributes(*required_attributes)
        plot_function(file, label, params)


        
    