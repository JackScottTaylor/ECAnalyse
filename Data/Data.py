import datetime
import numpy as np

class Data:
    def __init__(self):
        # This is the generic data object.
        # The attributes below are generally more defined for individual child classes.
        self.data = {}
        self.data_names = []
        self.time_format = ''
        self.t_data_name = ''
        self.start_time, self.end_time = 0, 0
        self.data_type = 'Data'
        self.plot_params = {} # Dictionary used for storing plot parameters.
        self.t_data_name = '' # If the data contains time data, set this to the correct data_name.


    def __add__(self, other):
        # This function is used to combine two Data objects.
        # The two data objects should be of the same type.
        # They must also have the same data_names.
        # A new Data object of the same type is first created.
        combined_data = type(self)()
        combined_data.data_names = self.data_names
        
        # If both start_times are datetime objects then new_start_time is the earliest of the two.
        # If both start_times are floats or integers then new_start_time is the smallest of the two.
        if type(self.start_time) == type(other.start_time):
            earliest_start_time = min(self.start_time, other.start_time)
        # Else if one is a datetime object and the other is a float or integer, then set new_start_time
        # to the datetime object.
        elif type(self.start_time) == datetime.datetime: earliest_start_time = self.start_time
        else: earliest_start_time = other.start_time
        # Set the start_time of the new object to the earliest_start_time.
        combined_data.start_time = earliest_start_time

        # If there is a data_name corresponding to time, then convert elapsed time in both files
        # to elapsed time relative to the new_start_time.
        if self.t_data_name in self.data_names:

            # Find the earliest_start_time in terms of elapsed time for each file.
            # If a start_time is a float or integer, then it is already elapsed time.
            if type(self.start_time) == datetime.datetime:
                self_relative_start_time = self.convert_datetime_to_elapsed_time(earliest_start_time)
            else: self_relative_start_time = - self.start_time

            if type(other.start_time) == datetime.datetime:
                other_relative_start_time = other.convert_datetime_to_elapsed_time(earliest_start_time)
            else: other_relative_start_time = - other.start_time

            # Convert the time data to elapsed time relative to the new_start_time.
            self_times = self.data[self.t_data_name] - self_relative_start_time
            other_times = other.data[other.t_data_name] - other_relative_start_time

            # Combine the time data and set the end_time of the new object.
            combined_data.data[self.t_data_name] = np.concatenate((self_times, other_times))
            combined_data.end_time = combined_data.convert_elapsed_time_to_datetime(combined_data.data[self.t_data_name][-1])

        # For all other data_names, concatenate the data arrays.
        for data_name in combined_data.data_names:
            if data_name == combined_data.t_data_name: continue
            combined_data.data[data_name] = np.concatenate((self.data[data_name], other.data[data_name]))

        # Set the common attributes of the new object.
        combined_data.set_commonly_accessed_attributes()
        # Reutrn the new object.
        return combined_data


    def convert_absolute_time_to_elapsed_time(self, time):
        # This function takes an absolute time and converts it to elapsed time.
        # Converted to datetime object using self.time_format.
        # If self.start_time not already set, then sets provided time to start_time.
        datetime_object = datetime.datetime.strptime(time, self.time_format)
        if self.start_time == 0: self.start_time = datetime_object
        return (datetime_object - self.start_time).total_seconds()
    

    def convert_datetime_to_elapsed_time(self, time):
        # This function takes a datetime object and converts it to elapsed time.
        # If self.start_time is not set, then an error is raised.
        if self.start_time == 0:
            raise ValueError(
                'Absolute start_time not defined for data object. Cannot convert datetime to elapsed time.'
            )
        return (time - self.start_time).total_seconds()
    

    def convert_elapsed_time_to_datetime(self, time):
        # This function takes an elapsed time in seconds and, using self.start_time,
        # converts this to an absolute time.
        # If self.start_time is not set, then the elapsed time is returned.
        if self.start_time == 0: return time
        return self.start_time + datetime.timedelta(seconds=time)
    

    def set_attributes(self, data_names, attribute_aliases):
        # This function takes a list of data_names and a list of attribute_aliases.
        # If data_name is a key in self.data then the data_list is set as an attribute
        # of the Data object using the provided alias.
        for data_name, attribute_alias in zip(data_names, attribute_aliases):
            if data_name in self.data_names: setattr(self, attribute_alias, self.data[data_name])


    def set_commonly_accessed_attributes(self):
        # Each child class will have a different set of commonly accessed attributes.
        # This function is overwritten in each child class.
        self.set_attributes(
            [],
            []
        )

    
    def in_time_range(self, start, end):
        # This function is very similar to in_data_range, but just for time data. Time is slightly
        # more complicated as you may want to describe time range in absolute time whereas the time
        # data is always stored as elapsed time.
        
        # First check that the object has time data, this should always be stored as an attribute
        # stored as self.t.
        if not hasattr(self, 't'):
            raise ValueError(
                f'{type(self)} object does not contain time data. Cannot determine time range.'
            )
        
        # If start or end is a datetime object, then convert to elapsed time.
        # convert_datetime_to_elapsed_time raises an error if start_time is not defined.
        if type(start) == datetime.datetime: start = self.convert_datetime_to_elapsed_time(start)
        if type(end) == datetime.datetime: end = self.convert_datetime_to_elapsed_time(end)

        # Now check that start and end are both either floats or ints, as they should now correspond
        # to elapsed time. If not then raise an error.
        if type(start) != float and type(start) != int:
            raise ValueError(
                'Start of time range must be either a float or an integer'
            )
        if type(end) != float and type(end) != int:
            raise ValueError(
                'End of time range must be either a float or an integer'
            )
        
        # Now use in_data_range method to extract data within the time range.
        return self.in_data_range('t', start, end)
    
    
    def in_data_range(self, data_name, start, end):
        # This function returns a new data object containing only the data stored in the range
        # defined by start <= x <= end for the provided data_name.
        # Data_name can be and data_name stored in self.data or can be common attribute.

        # If data_name is not in self.data_names, then check if it is an attribute.
        # If not then raise an error.
        if data_name not in self.data_names:
            if not hasattr(self, data_name):
                raise ValueError(
                    f'{data_name} is not a data_name or common attribute of the Data object.'
                )
            else:
                # If data_name is attribute then check that attribute is a numpy array.
                # If not then raise an error.
                if type(getattr(self, data_name)) != np.ndarray:
                    raise ValueError(
                        f'{data_name} attribute is not an array.'
                    )
                else:                                                               
                    data = getattr(self, data_name)
        # If data_name is in self.data_names, then set data to the data stored in self.data.
        else:
            data = self.data[data_name]


        # Create a new blank object of the same type as self.
        new_data = type(self)()
        new_data.data_names = self.data_names
        data_mask = (data >= start) & (data <= end)
        for data_name in self.data_names: new_data.data[data_name] = self.data[data_name][data_mask]

        # If the data contains time_data, then need to set start and end times and convert the 
        # elapsed time_data to elapsed time since start of new_data.
        if new_data.t_data_name in new_data.data_names:
            new_data.start_time = self.convert_elapsed_time_to_datetime(new_data.data[new_data.t_data_name][0])
            new_data.end_time   = self.convert_elapsed_time_to_datetime(new_data.data[new_data.t_data_name][-1])
            new_data.data[new_data.t_data_name] -= new_data.data[new_data.t_data_name][0]

        # Set the common attributes of the new_data object.
        new_data.set_commonly_accessed_attributes()

        return new_data