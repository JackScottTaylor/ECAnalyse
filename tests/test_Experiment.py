from ECAnalyse.Experiment import Experiment
from ECAnalyse.Data import Data, TIME_PLACEHOLDER
from ECAnalyse.File_Types import ECLab_File

import os
import pathlib
import numpy as np
import pytest

from datetime import datetime

# Get repo paths
REPO_PATH = pathlib.Path(__file__).parent.resolve()
DATA_DIR = os.path.join(REPO_PATH, 'data_files')

@pytest.fixture
def csv_path_1():
    return os.path.join(DATA_DIR, 'negative+positive+switching+negative+5min_holds_01_MB_C08.csv')

@pytest.fixture
def csv_path_2():
    return os.path.join(DATA_DIR, 'negative+positive+switching+negative+5min_holds_02_CV_C08.csv')

def test_experiment_initialization(csv_path_1, csv_path_2):
    file1 = ECLab_File(csv_path_1)
    file2 = ECLab_File(csv_path_2)

    assert file1.t[0] == 0.0
    assert file2.t[0] == 0.0
    
    experiment = Experiment(file1, file2)
    
    assert len(experiment.files) == 2
    assert isinstance(experiment.files[0], Data)
    assert isinstance(experiment.files[1], Data)

    correct_start_time = '03/20/2025 16:32:05.155000'
    correct_start_time = datetime.strptime(correct_start_time, "%m/%d/%Y %H:%M:%S.%f")
    assert experiment.start_time == correct_start_time
    assert experiment.files[0].start_time == correct_start_time
    assert experiment.files[1].start_time == correct_start_time

    assert experiment.files[0].t[0] == 0.0
    assert experiment.files[1].t[0] != 0.0
    