# The Data Class

This class is used as the most basic object for storing data from an experiment. The class can be loaded via `from ECAnalyse.Data import Data`.

# Attributes

The `Data` object is initialised with various attributes which serve as a template for child classes.

```python
self.data                       = {}
self.data_names                 = []
self.time_format                = ''
self.t_data_name                = ''
self.start_time, self.end_time  = 0, 0
self.data_type                  = 'Data'
self.plot_params                = {}
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

# Methods

The `Data` class comes with a variety of methods that are inherited by all children and should not be redefined.

## `__add__`

This method defines how the `+` operator works in relation to `Data` objects. It allows for the following operation.

```python
data1 = Data()
data2 = Data()
data_combined = data1 + data2
```

>[!CAUTION]
>The two `Data` objects must have the same set of `data_names`.

