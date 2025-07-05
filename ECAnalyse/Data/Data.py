import datetime
import numpy as np
import warnings

from typing import Union, List

# Define a placeholder time such that the Data object can use start_time and
# end_time if not defined by the user or by data.
TIME_PLACEHOLDER = datetime.datetime(2000, 1, 21, 12, 0)

class Data:
    '''
    This is a general class designed for holding data from an experiment.
    Different file types will inherit from this class and implement their own
    methods for reading data from files.

    Data stored in data dictionary, where keys are data_names and the values are
        numpy arrays containing the corresponding data.
    Attribute aliases is a dictionary where the keys correspond to set
        attributes and the values are the corresponding data_names. For example
        file might store time under 'Absolute Time' but the user has set the 
        common attribute 't' to refer to this data.
    time_format is a string that describes how datetimes are formatted in the 
        data that is read in, if it is included.
    t_data_name is the data_name that corresponds to time data, if it exists.
    start_time and end_time are the start and end times of the data which will
        be set to the earliest and latest datetimes in the data. If there is no
        time data or time data is only in elapsed time, then these are set to 
        TIME_PLACEHOLDER.
    data_type is a string that describes what class of data this is.
    '''
    def __init__(self):
        self.data:              dict               = {}
        self.attribute_aliases: dict               = {}
        self.time_format:       str                = ''
        self.t_data_name:       str                = ''
        self.start_time:        datetime.datetime  = TIME_PLACEHOLDER
        self.data_type:         str                = 'Data'


    def summary(self):
        '''
        Provides a summary of the Data object
        '''
        duration = (self.end_time - self.start_time).total_seconds()
        print(f"Data Type:       {self.data_type}")
        print(f"Start Time:      {self.start_time}")
        print(f"End Time:        {self.end_time}")
        print(f"Duration:        {duration} seconds")
        print(f"Data Fields:     {self.data_names}")
        print(f"Aliases:         {self.attribute_aliases}")
        print(f"Number of Rows:  {len(next(iter(self.data.values()), []))}")


    @property
    def data_names(self) -> List[str]:
        '''
        This property returns the keys of the data dictionary

        :return: A list of data_names (keys of the data dictionary).
        '''
        return list(self.data.keys())
    
    @property
    def end_time(self) -> datetime.datetime:
        '''
        This property returns the end_time of the Data object by adding the
        last value in the time data (in seconds) to the start_time. If no time
        data then it returns the start_time and a warning is raised.
        
        :return: The end_time of the Data object.
        '''
        if self.t_data_name not in self.data_names:
            warnings.warn(
                f'{type(self)} object does not contain time data. '
                'Returning start_time as end_time.'
            )
            return self.start_time
        return self.start_time + datetime.timedelta(
            seconds=self.data[self.t_data_name][-1]
        )


    def set_start_time(
        self,
        start_time: datetime.datetime = TIME_PLACEHOLDER,
        ):
        '''
        This method sets the start_time of the Data object to the provided
        datetime object. If end_time_changes it also changes the end_time
        such as the value of end_time - start_time is conserved. If the
        start_time provided is not datetime object then a ValueError is raised.
        
        :param start_time: The start time to set the Data object to
        '''
        if type(start_time) != datetime.datetime:
            raise ValueError(
                f'Start time must be a datetime object, not {type(start_time)}.'
            )
        self.start_time = start_time

    def set_end_time(
        self,
        end_time: datetime.datetime = TIME_PLACEHOLDER
        ):
        '''
        end_time is a property which can not be set, so instead this method 
        sets the start_time such that when called, self.end_time will yield
        the desired value.
        
        :param end_time: The start time to set the Data object to
        '''
        if type(end_time) != datetime.datetime:
            raise ValueError(
                f'End time must be a datetime object, not {type(end_time)}.'
            )
        time_difference = (end_time - self.end_time).total_seconds()
        self.start_time = self.start_time + datetime.timedelta(
                                                    seconds = time_difference
                                                    )

    def __add__(self, other):
        '''
        This method allows for two Data objects to be combined using the +
        operator. 

        Both Data objects should be the same type.
        '''
        # Check that both objects are same type, if not then raise error.
        if type(self) != type(other):
            raise TypeError(
                f'Cannot combine {type(self)} and {type(other)} objects. '
                'Both objects must be of the same type.'
            )
        # Initialise new object of the same type as self.
        combined_data = type(self)()

        # Check that both objects have the same data_names, if not raise error.
        if set(self.data_names) != set(other.data_names):
            raise ValueError(
                f'Cannot combine {type(self)} and {type(other)} objects. '
                'Both objects must have the same data_names.'
            )

        # The start_time of the new object is set to the earliest start_time of
        # the two objects. If start_time for exactly one is TIME_PLACEHOLDER,
        # then raise warning as this is likely an error.
        if [self.start_time, other.start_time].count(TIME_PLACEHOLDER) == 1:
            warnings.warn(
                f'One of the passed objects ({type(self)} or {type(other)}) ' +
                f'has a start_time set to the placeholder value while the ' +
                f'other does not. Time combination is therfore likelky wrong.'
            )

        # Set the start and end times of the new object based on the self and 
        # other objects.
        combined_data.set_start_time(
            start_time = min(self.start_time, other.start_time)
        )
        
        # At this point we know that both objects have the same data_names
        # therefore we can check if there is time data by just checking if
        # time is recorded in the first data file.
        if self.t_data_name in self.data_names:
            # Now we have to calculate the time differences for the two files
            # so that we can record data as time elapsed from the new file's
            # start time

            self_rel_start_time = self.convert_datetime_to_elapsed_time(
                                                       combined_data.start_time
                                                       )
            other_rel_start_time = other.convert_datetime_to_elapsed_time(
                                                       combined_data.start_time
                                                       )
            # Apply reference to the two sets of time data
            self_times  = self.data[self.t_data_name]   - self_rel_start_time
            other_times = other.data[other.t_data_name] - other_rel_start_time

            # Combine the time data and set the end_time of the new object.
            combined_data.data[self.t_data_name] = np.concatenate(
                                                      (self_times, other_times)
                                                      )

        # For all other data_names, concatenate the data arrays and add to data
        for data_name in self.data_names:
            if data_name == combined_data.t_data_name: continue
            combined_data.data[data_name] = np.concatenate(
                                   (self.data[data_name], other.data[data_name])
                                   )

        # Set the common attributes of the new object.
        combined_data.set_commonly_accessed_attributes()
        # Reutrn the new object.
        return combined_data


    def convert_absolute_time_to_elapsed_time(self, time: str) -> float:
        '''
        This function takes a time representing a date in the format defined in
        self.time_format. Converts it to a datetime object, calculates and then
        returns the time in seconds between self.start_time and the time given.

        :param time: String representing date in format of self.date_format
        :return: Time between self.start_time and given time in seconds
        '''
        datetime_object = datetime.datetime.strptime(time, self.time_format)
        return self.convert_datetime_to_elapsed_time(datetime_object)
    

    def convert_datetime_to_elapsed_time(
            self,
            time: datetime.datetime
            ) -> float:
        '''
        Takes a datetime object and calculates the time between self.start_time
        and the given time and then returns this value.

        :param time: datetime object corresponding to a given date
        :return: Time in seconds between self.start_time and given time
        '''
        return (time - self.start_time).total_seconds()
    

    def convert_elapsed_time_to_datetime(
            self,
            time: float
            ) -> datetime.datetime:
        '''
        Takes a time in seconds and returns the datetime object corresponding to
        time seconds since self.start_time

        :param time: Time in seconds since self.start_time
        :return: datetime object cprresponding to time seconds since
            self.start_time
        '''
        return self.start_time + datetime.timedelta(seconds=time)
    

    def set_attributes(
            self,
            data_names: List[str],
            attribute_aliases: List[str]
            ):
        '''
        Takes list of data names and list of aliases. If data name is in
        self.data_names then it sets the associated data as an attribute of
        the object with the attribute name being the alias.

        :param data_names: List of data names to create aliases for
        :param attribute_aliases: The corresponding aliases
        '''
        for data_name, attribute_alias in zip(data_names, attribute_aliases):
            if data_name in self.data_names:
                setattr(self, attribute_alias, self.data[data_name])
                self.attribute_aliases[attribute_alias] = data_name


    def set_commonly_accessed_attributes(self):
        '''
        Every child class of Data should overwrite this function with the
        common attributes of that Data type.
        It is necessary to include here so it can be called generally when
        combining or slicing Data objects.
        '''
        self.set_attributes(
            [],
            []
        )


    def in_data_range(
            self,
            data_name: str,
            minimum:   float,
            maximum:   float
            ):
        '''
        Returns a new data object the same type as self containing only the data
        where the data corresponding to data_name falls in the closed region of
        [minimum, maximum]

        :param data_name: The data which to filter by
        :param minimum: The minimum value the data should take
        :param maximum: The maximum value the data should take
        '''
        # Find key for data_dict corresponding to data required. If not found
        # then error is raised by self.data_key method.
        data_dict_key = self.data_key(data_name)
        data          = self.data[data_dict_key]

        # Create a new blank object of the same type as self.
        new_data  = type(self)()
        # Find the indices where the inequalities are satisfied
        data_mask = (data >= minimum) & (data <= maximum)
        # Add only the correct data to the new data file
        for data_name in self.data_names:
            new_data.data[data_name] = self.data[data_name][data_mask]

        # In assigning the start_time, we will use the same start_time as self
        # as there is always the option to zero the time later
        if self.t_data_name in self.data_names:
            time_key = self.t_data_name
            new_data.start_time = self.start_time
        # Set the common attributes of the new_data object.
        new_data.set_commonly_accessed_attributes()
        return new_data
    

    def zero_time(self):
        '''
        This method sets the first value in recorded data to be equal to zero
        and adjusts the start and end times accordingly
        '''
        # If no time data then raise error
        if self.t_data_name not in self.data_names:
            raise ValueError(
                f'{type(self)} object does not contain time data.'
            )
        delta_t = self.data[self.t_data_name][0]
        self.data[self.t_data_name] -= delta_t
        self.start_time = self.start_time + datetime.timedelta(seconds=delta_t)

    
    def in_time_range(
            self,
            start: Union[float, datetime.datetime],
            end:   Union[float, datetime.datetime]
            ):
        '''
        Returns a new Data object with only the data corresponding to the times
        between start and end.
        Start and end can either be floats corresponding to seconds elapsed
        since self.start_time, or they can be datetime objects

        :param start: The earliest time allowed
        :param end: The latest time allowed
        '''
        if self.t_data_name not in self.data_names:
            raise ValueError(
                f'{type(self)} object does not contain time data.'
            )
        
        # If start or end are datetime objects then convert them in to elapsed
        # time
        if type(start) == datetime.datetime:
            start = self.convert_datetime_to_elapsed_time(start)
        if type(end) == datetime.datetime:
            end   = self.convert_datetime_to_elapsed_time(end)
        
        # Now use in_data_range method to extract data within the time range.
        return self.in_data_range(self.t_data_name, start, end)
    
    
    def data_key(self, d: str) -> str:
        '''
        This function returns the key for the data_name provided.
        
        If d is in self.data_names then it is returned.
        If d is a set attribute, then the corresponding data_name
        is returned from self.attribute_aliases.
        
        :param d: The name of the data to get the key for.
        :type d: str
        :return: The key for the data_name provided.
        :rtype: str
        '''
        if   d in self.data_names: return d
        elif d in self.attribute_aliases: return self.attribute_aliases[d]
        else: raise ValueError(
            f'{d} is not a data_name or common attribute of the Data object.'
        )
    
    def rolling_average(
            self, *data_names: str, w: int = 1
            ) -> Union[np.ndarray, tuple[np.ndarray, ...]]:
        '''
        This function calculates the rolling average of the data_names provided.

        :param data_names: The names of the data to calculate the rolling
            average for.
        :type data_names: str
        :keyword w: The window size for the rolling average, default is 1.
        :type w: int
        :return: Either a single numpy array or a tuple of numpy arrays
        '''
        kernel = np.ones(w) / w  # Create a kernel for the rolling average.
        roll_av_data = []
        for data_name in data_names:
            key = self.data_key(data_name)
            assert w > 0, 'Window size must be greater than 0.'
            # Apply the convolution to the data.
            roll_av_data.append(np.convolve(
                self.data[key], kernel, mode='valid'))
        return tuple(roll_av_data) if len(roll_av_data) > 1 else roll_av_data[0]


