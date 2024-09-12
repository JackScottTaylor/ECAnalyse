# The Data Class

This class is used as the most basic object for storing data from an experiment. The class can be loaded via `from ECAnalyse.Data import Data`.

# Initialised Attributes

The `Data` object is initialised with various attributes which serve as a template for child classes.

```python
self.data                       = {}
self.data_names                 = []
self.time_format                = ''
self.t_data_name                = ''
self.start_time, self.end_time  = 0, 0
self.data_type                  = 'Data'
self.plot_params                = {}
self.t_data_name                = ''
```

## `self.data`

This is initialised as an empty dictionary. In general this is where data will be stored with a key corresponding to the data name and the value should be a numpy array

## `self.data_names`

An empty array which will contain the data names once `self.data` is filled.

## `self.time_format`

This is initialised as an empty string. 

For many experiments, the time data is exported as a date. As we want to store numpy arrays, best practise is to convert the dates into elapsed times and store the start date of the data. To do this, the `datetime` library is used to convert a date string into a `datetime` object. To do this it needs to know the format of the date in the data, which is stored in this attribute. For example, if the date is exported as such `21/01/2000 12:30:05.3`, then `self.time_format =  "%d/%m/%y $H:%M:%S.%f"`.

## `self.start_time`

Initialised as zero.

If data to be read in contains time data in the form of dates, then `self.start_time` is set to a `datetime` object corresponding to the first time data point. Otherwise it remains set to zero.

## `self.end_time`

Initialised to zero.

As with `self.start_time`, only changed if data to be read contains time data in the form of dates, in which case this attribute is set to a `datetime` object corresponding to the last time point.

## `self.data_type`
Initialised to `'Data'`.

Child classes should set this attribute to however they want to be styled. This attribute exists so that functions can easily check what kind of `Data` object they are dealing with, without having to import all of the possible object types.

## `self.plot_params`

Initialised as an empty dictionary. 

This attribute is used to assist in plotting figures. The idea is that if you pass many `Data` objects to a figure making function, then the function will need to know what style to use for each object. Therefore this attribute should contain keys which correspond to matplotlib key-word arguments and the values correspond to the value you want to pass.

For example:

```python
data_1 = Data()
Data.plot_params = {
    'color':        'black',
    'linestyle':    '--'
}
```

## `self.t_data_name`

Initialised to empty string.

If a child class loads time data, then this should be set to the data_name under which time data is stored. The purpose of this attribute is such that any functions can always find where time data is stored, even if different child classes store it under a different data_name.

# Methods

The `Data` class comes with a variety of methods that are inherited by all children and should not be redefined.

## `__add__(self, other)`

This method defines how the `+` operator works in relation to `Data` objects. It allows for the following operation, where the two `Data` objects are combined to return a new `Data` object, which is the same type as the first `Data` object passed, i.e. `type(data_combined) = type(data1)`.

```python
data1 = Data()
data2 = Data()
data_combined = data1 + data2
```

>[!CAUTION]
>The two `Data` objects must have the same set of `data_names`. 

The method checks whether the `Data` object contains time data by checking whether to see if it has the attribute `self.t`. All `Data` objects which store time data should have `t` as an attribute which contains the numpy array corresponding to elapsed time.

If `start_time` is a `datetime` object for both, then `data_combined.start_time` is set to the earlier of the two start_times.

If `start_time` is zero for both, then `data_combined.start_time` is also set to zero.

If `start_time` is a `datetime` object for one and zero for the other then `data_combined.start_time` is set to the `datetime` value.

The method handles converting the time data in each respective object so that it is elapsed time since `data_combined.start_time`. This ensures that all the time points remain accurate.

Before the `combined_data` object is returned, `combined_data.set_commonly_accessed_attributes()` is ran. Remember that `type(data_combined) = type(data1)` such that `set_commonly_accessed_attributes` is already defined.

## `convert_absolute_time_to_elapsed_time(self, time)`
**Arguments:**

- `time` : A string corresponding to a date in the same format as `self.time_format`.

**Returns:**

- `elapsed_time` : A float corresponding to elapsed time (in seconds) since `self.start_time`.


**Methodology:**

- Converts `time` to `datetime` object using `self.time_format`
- If `self.start_time` equal to zero, sets to this `datetime` object.
- Calculates time elapsed since `self.start_time` in seconds.


## `convert_elapsed_time_to_datetime(self, time)`

**Arguments:**

- `time` : Float corresponding to a time in seconds elapsed since `self.start_time`

**Returns:**

- `absolute_time` : `datetime` object corresponding to date which provided elapsed time represents.

**Methodology:**

- Adds `time` seconds to `self.start_time` and returns the result.


## `set_attributes(self, data_names, attribute_aliases)`

**Arguments:**

- `data_names` : Array of strings.
- `attribute_aliases` : Array of strings
  
**Methodology:**

 - Iterates through `data_names` and `attribute_aliases` together as name and alias.
 - If name in `self.data_names` then sets the alias as an attribute of the object with value corresponding to `self.data_names[name]`

**Common Use:**

- If time data included in `Data` object, then should ensure that time data can be accesed via `self.t` as this is used for various other methods.
- Some child classes may have data that is very routinely accessed, such as voltage, in which case applying this method can increase readability.

## `set_commonly_accessed_attributes(self)`

**Common Use:**

- This method should be overwritten by child classes, so that this method may be run at the end of initialisation, automatically making commonly accessed data attributes of the class.

## `in_time_range(self, start, end)`

**Arguments:**

- `start` : float or `datetime`. Defines the start time for which you want to extract the data.
- `end` : float or `datetime`. Defines the end time for which you want to extract the data

**Returns:**

- Object the same type as `self` containing data only from the range defined by `start` and `end`

**Methodology:**

- If `start` or `end` are `datetime` objects then converts them respectively to elapsed times using the `self.convert_datetime_to_elapsed_time` method.
- Uses the `self.in_data_range` method to return the new `type(self)` object containing only the data from the defined time range.


##  `in_data_range(self, data_name, start, end)`

**Arguments:**

- `data_name` : `string` corresponding to either value in `self.data_names` or an attribute of `self` which contains data.
- `start` : `float` corresponding to minimum value of data requested
- `end` : `float` corresponding to maximum value of data requested

**Returns:**

- Object the same type as `self` with only the data where the data corresponding to `data_name` is in the closed range defined by `start` and `end`.

**Methodology:**

- Checks that `data_name` is either in `self.data_names` or that it is an attribute of `self` and extracts the corresponding data.
- Creates a mask for the data defined by `start` and `end`. If `start` > `end` then no value will satisfy and returned object will contain no data. Range is closed, therefore values which exactly equal either `start` or `end` will be included.
- The indices of values in the extracted data which extract the mask are found, and these indices are used to generate filtered data arrays for all of the data stored in `self.data`.
- The new `Data` object is initialised with these filtered data arrays, `set_commonly_accessed_attributes` is called and the object then returned.

**Common Use:**

An example may be that you have a Data object, `example_data`, which has cycles of data stored, with the specific cycle stored in `example_data.c`. If you then want a new object which only contains the data corresponding to the second and third cycles, you may do it as follows.

```python
filtered_data = example_data.in_data_range('c', 2, 3)
```

