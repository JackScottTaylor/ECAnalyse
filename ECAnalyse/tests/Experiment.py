import os
import pathlib
import datetime
import numpy as np
repository_path = pathlib.Path(__file__).parent.resolve()
data_files_dir = os.path.join(repository_path, 'data_files')

from ..Data import Data
from ..File_Types import ECLab_File
from ..Experiment.Experiment import Experiment

def test_Experiment():
    # Test that the Experiment class can be initialized with Data objects.
    file1 = ECLab_File(os.path.join(data_files_dir, 'PAQ (5mM) TBAPF6 (0,1M) DMSO, N2 100 CO2 0, 100mVs-1, -1,86V-1V_C01.txt'))
    file2 = ECLab_File(os.path.join(data_files_dir, 'ACC-20, 1M Na2SO4, N2 10mlmin-1, CO2 2,5mlmin-1, 2,5rpm_C01.txt'))
    
    experiment = Experiment(file1, file2)


def test_sync_times():
    file1 = 'data_files/negative+positive+switching+negative+5min_holds_01_MB_C08.csv'
    file1 = ECLab_File(os.path.join(repository_path, file1))
    file2 = 'data_files/negative+positive+switching+negative+5min_holds_02_CV_C08.csv'
    file2 = ECLab_File(os.path.join(repository_path, file2))

    experiment = Experiment(file1, file2)
    experiment.sync_times()
    start = datetime.datetime.strptime('03/20/2025 16:32:05.155000', "%m/%d/%Y %H:%M:%S.%f")
    assert experiment.start_time == start, f"Expected {start}, got {experiment.start_time}"
    assert np.all(file1.start_time == start), f"Expected {start}, got {file1.start_time}"
    assert np.all(file2.start_time == start), f"Expected {start}, got {file2.start_time}"
    assert np.all(experiment.files[0].t == experiment.files[0].data['time/s'])
    assert np.all(experiment.files[1].t == experiment.files[1].data['time/s'])

    print(file1.t[0], file2.t[0])

