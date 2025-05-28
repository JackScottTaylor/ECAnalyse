import os
import pathlib
import datetime
import numpy as np
repository_path = pathlib.Path(__file__).parent.resolve()
data_files_dir = os.path.join(repository_path, 'data_files')
from ..Data import Data

def test_rolling_average():
    d1 = Data()
    d1.data = {
        'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'y': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
    }
    d1.data_names = ['x', 'y']
    d1.set_attributes(['x', 'y'], ['xalias', 'yalias'])

    assert np.allclose(
        d1.rolling_average('x', w=3), 
        np.array([2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
    )
    assert np.allclose(
        d1.rolling_average('y', w=3), 
        np.array([20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0])
    )

    assert np.allclose(
        d1.rolling_average('xalias', w=3), 
        np.array([2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
    )
    assert np.allclose(
        d1.rolling_average('yalias', w=3), 
        np.array([20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0])
    )

    x_av, y_av = d1.rolling_average('x', 'yalias', w=3)
    assert np.array_equal(x_av, d1.rolling_average('x', w=3))
    assert np.array_equal(y_av, d1.rolling_average('y', w=3))

