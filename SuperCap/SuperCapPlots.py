# This module contains the functions used for making plots for SuperCap experiments.
from ..custom_plt import custom_plt
plt = custom_plt()

def plot_GCD(*files, labels=[], use_params=False, ax=plt.gca()):
    # In GCD experiments, constant current is applied.
    # Voltage is plotted against time.

    # First fill labels with None until same size as files
    while len(labels) < len(files):
        labels.append(None)

    # If any of the files have a start_time which is not a datetime object, then have
    # to assume that times are already calibrated between files.
    corrected_time_required = True
    for file in files:
        if type(file.start_time) == float or type(file.start_time) == int:
            corrected_time_required = False
            break

    # Each file must be calibrated so that times are correct
    # Take the global start_time as the start_time fo the first file
    start_time = files[0].start_time

    for file, label in zip(files, labels):
        # Check that the object has both E and t attribues:
        if not hasattr(file, 'E') or not hasattr(file, 't'):
            raise AttributeError('The object must have both E and t attributes.')
        if corrected_time_required:
            corrected_time = file.t - file.convert_datetime_to_elapsed_time(start_time)
        else: 
            corrected_time = file.t
        if use_params: ax.plot(corrected_time, file.E, label=label, **file.plot_params)
        else: ax.plot(corrected_time, file.E, label=label)

    ax.set_xlabel('Time / s')
    ax.set_ylabel('Voltage / V')
        
        