# This module contains some functions that plot functions
# may commonly wish to use.

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