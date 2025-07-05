import os
import pathlib
import datetime
import numpy as np
import pytest

from ECAnalyse.Data import Data
from ECAnalyse.Data.Data import TIME_PLACEHOLDER
from ECAnalyse.File_Types import ECLab_File

# Get repo paths
REPO_PATH = pathlib.Path(__file__).parent.resolve()
DATA_DIR = os.path.join(REPO_PATH, 'data_files')

# --------------------------------------
# Fixtures
# --------------------------------------

@pytest.fixture
def file_path_1():
    return os.path.join(DATA_DIR, 'PAQ (5mM) TBAPF6 (0,1M) DMSO, N2 100 CO2 0, 100mVs-1, -1,86V-1V_C01.txt')

@pytest.fixture
def file_path_2():
    return os.path.join(DATA_DIR, 'ACC-20, 1M Na2SO4, N2 10mlmin-1, CO2 2,5mlmin-1, 2,5rpm_C01.txt')

@pytest.fixture
def csv_path_1():
    return os.path.join(DATA_DIR, 'negative+positive+switching+negative+5min_holds_01_MB_C08.csv')

@pytest.fixture
def csv_path_2():
    return os.path.join(DATA_DIR, 'negative+positive+switching+negative+5min_holds_02_CV_C08.csv')


# --------------------------------------
# Test: reading ECLab text files
# --------------------------------------

def test_reading_txt_files(file_path_1, file_path_2):
    file1 = ECLab_File(file_path_1)
    file2 = ECLab_File(file_path_2)

    assert file1.data_names == ['Ewe/V', 'I/mA', 'cycle number']
    assert file2.data_names == ['time/s', 'Ewe/V', 'I/mA', 'cycle number']

    assert file1.start_time == TIME_PLACEHOLDER
    assert file1.end_time == TIME_PLACEHOLDER
    assert file2.start_time == datetime.datetime.strptime('07/11/2024 10:31:05.3322', "%m/%d/%Y %H:%M:%S.%f")
    assert file2.end_time == datetime.datetime.strptime('07/12/2024 13:50:07.7127', "%m/%d/%Y %H:%M:%S.%f")


# --------------------------------------
# Test: reading CSV ECLab files
# --------------------------------------

def test_reading_csv_files(csv_path_1, csv_path_2):
    file1 = ECLab_File(csv_path_1)
    file2 = ECLab_File(csv_path_2)

    expected_names = ['time/s', 'Ewe/V', 'Pressure/bar (on Analog In1)', 'I/mA', 'cycle number']
    assert file1.data_names == expected_names
    assert file2.data_names == expected_names

    assert file1.t[0] == 0.0
    assert file1.start_time == datetime.datetime.strptime('03/20/2025 16:32:05.155000', "%m/%d/%Y %H:%M:%S.%f")
    assert pytest.approx(file1.P[0]) == 0.97912329435

    assert file2.t[0] == 0.0
    assert file2.start_time == datetime.datetime.strptime('03/21/2025 04:33:06.786000', "%m/%d/%Y %H:%M:%S.%f")
    assert pytest.approx(file2.P[0]) == 0.9132810831


# --------------------------------------
# Test: in_time_range
# --------------------------------------

def test_in_time_range(file_path_2):
    file = ECLab_File(file_path_2)

    # Full-range
    start = file.start_time - datetime.timedelta(seconds=5)
    end   = file.end_time + datetime.timedelta(seconds=5)
    new = file.in_time_range(start, end)

    for name in file.data_names:
        assert np.array_equal(file.data[name], new.data[name])

    # Trimmed range
    start = file.start_time + datetime.timedelta(seconds=5)
    end   = file.end_time - datetime.timedelta(seconds=5)
    new = file.in_time_range(start, end)

    assert new.start_time == file.start_time

    new.zero_time()
    assert new.start_time == file.start_time + datetime.timedelta(seconds=5)


# --------------------------------------
# Test: in_data_range
# --------------------------------------

def test_in_data_range():
    df = Data()
    df.data = {
        'time/s': np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
        'other':  np.array([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    }
    df.set_attributes(['time/s', 'other'], ['t', 'o'])

    result = df.in_data_range('time/s', 3, 7)
    assert np.array_equal(result.data['time/s'], np.array([3, 4, 5, 6, 7]))
    assert np.array_equal(result.data['other'],  np.array([30, 40, 50, 60, 70]))

    result = df.in_data_range('t', 3, 7)
    assert np.array_equal(result.data['time/s'], np.array([3, 4, 5, 6, 7]))

    result = df.in_data_range('t', 0, 11)
    assert np.array_equal(result.data['time/s'], df.data['time/s'])

    with pytest.raises(ValueError, match='is not a data_name or common attribute'):
        df.in_data_range('xxx', 3, 7)


# --------------------------------------
# Test: cycles
# --------------------------------------

def test_ECLab_cycles(file_path_1, file_path_2):
    file1 = ECLab_File(file_path_1)
    file2 = ECLab_File(file_path_2)

    cycles_1_2 = file1.cycles(1, 2)
    assert len(cycles_1_2.E) == 11417

    cycles_1_2_file2 = file2.cycles(1, 2)
    expected_end = datetime.datetime.strptime('07/11/2024 15:41:35.6007', "%m/%d/%Y %H:%M:%S.%f")
    assert cycles_1_2_file2.end_time == expected_end
