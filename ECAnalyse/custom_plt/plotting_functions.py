import matplotlib.pyplot as plt

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..Data import Data
    from matplotlib.axes import Axes

def rolling_average_plot(
        ax: 'Axes',
        file: 'Data',
        x_name: str,
        y_name: str,
        rolling_average: bool = False,
        window_size: int = 10,
        label: str = '',
        **kwargs
    ) -> 'Axes':
    '''
    Plots the data with an optional rolling average. If rolling average True
    then raw data is plotted with transparency and the rolling avaerage is 
    plotted as well. Only the non-transparent data has a label

    :param ax: matplotlib Axes object to plot on.
    :param file: Data object containing the data to plot.
    :param x_name: Name of the x-axis data.
    :param y_name: Name of the y-axis data.
    :param rolling_average: If True, applies a rolling average to the data.
    :param window_size: Size of the rolling average window if using.
    :param label: Label for the plot. If rolling average is True, this label
        will only be applied to the non-transparent data.
    :param kwargs: Additional keyword arguments to pass to the plot.
    :return: The Axes object with the plot.
    '''
    x_key = file.data_key(x_name)
    y_key = file.data_key(y_name)
    if rolling_average:
        kwargs['alpha'] = 0.25
        x, y = file.data[x_key], file.data[y_key]
        ax.plot(x, y, **kwargs)
        kwargs['alpha'] = 1.0
        x, y = file.rolling_average(x_key, y_key, w=window_size)
        ax.plot(x, y, label=label, **kwargs)
    else:
        x, y = file.data[x_key], file.data[y_key]
        ax.plot(x, y, label=label, **kwargs)
    return ax