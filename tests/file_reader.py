import os
import pathlib
import datetime
import numpy as np
repository_path = pathlib.Path(__file__).parent.resolve()
data_files_dir = os.path.join(repository_path, 'data_files')

# This comment is added to demonstarte how to use branches.

from ..Data import Data
from ..File_Types import ECLab_File

def test_reading_ECLab_Files():
    # This test ensures that ECLab_File can correctly extract data from an ECLab file.
    file1 = 'data_files/PAQ (5mM) TBAPF6 (0,1M) DMSO, N2 100 CO2 0, 100mVs-1, -1,86V-1V_C01.txt'
    file2 = 'data_files/ACC-20, 1M Na2SO4, N2 10mlmin-1, CO2 2,5mlmin-1, 2,5rpm_C01.txt'
    
    file1 = ECLab_File(os.path.join(repository_path, file1))
    file2 = ECLab_File(os.path.join(repository_path, file2))

    assert file1.data_names == ['Ewe/V', 'I/mA', 'cycle number'], "Data names are not correct for file 1."
    assert file2.data_names == ['time/s', 'Ewe/V', 'I/mA', 'cycle number'], "Data names are not correct for file 2."

    assert file1.start_time == 0, f'Start_time should equal 0 for file_1 but equals {file1.start_time}'
    assert file2.start_time == datetime.datetime.strptime('07/11/2024 10:31:05.3322', "%m/%d/%Y %H:%M:%S.%f"), f'Start_time should equal 07/11/2024 10:31:05.3322 for file_2 but equals {file2.start_time}'
    assert file2.end_time == datetime.datetime.strptime('07/12/2024 13:50:07.7127', "%m/%d/%Y %H:%M:%S.%f"), f'End_time should equal 07/12/2024 13:50:07.7127 for file_2 but equals {file2.end_time}'


def test_in_time_range():
    # This test ensures that the in_time_range function works correctly.
    file1 = 'data_files/PAQ (5mM) TBAPF6 (0,1M) DMSO, N2 100 CO2 0, 100mVs-1, -1,86V-1V_C01.txt'
    file2 = 'data_files/ACC-20, 1M Na2SO4, N2 10mlmin-1, CO2 2,5mlmin-1, 2,5rpm_C01.txt'
    
    file1 = ECLab_File(os.path.join(repository_path, file1))
    file2 = ECLab_File(os.path.join(repository_path, file2))

    # Test 1: Test that if file has absolute start_time, then if absolute times beyond
    # range of data, then returned object contains all data.
    start   = file2.start_time - datetime.timedelta(seconds=5)
    end     = file2.end_time + datetime.timedelta(seconds=5)
    new     = file2.in_time_range(start, end)
    for data_name in file2.data_names:
        assert np.array_equal(file2.data[data_name], new.data[data_name]), f'Data for {data_name} is not equal for file_2.'

    # Test 2: Test that if file has absolute start_time, then if absolute times within
    # range of data, then returned object contains only data within that range.
    start   = file2.start_time + datetime.timedelta(seconds=5)
    end     = file2.end_time - datetime.timedelta(seconds=5)
    new     = file2.in_time_range(start, end)
    assert new.start_time == datetime.datetime.strptime('07/11/2024 10:31:10.3322', "%m/%d/%Y %H:%M:%S.%f"), f'Start_time should equal 07/11/2024 10:31:10.3322 for file_2 but equals {new.start_time}'
    assert new.end_time == datetime.datetime.strptime('07/12/2024 13:50:02.6775', "%m/%d/%Y %H:%M:%S.%f"), f'End_time should equal 07/12/2024 13:50:03.6775 for file_2 but equals {new.end_time}'


def test_in_data_range():
    # This test ensures that the in_data_range function works correctly.
    data_file = Data()
    data_file.data['time/s']    = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    data_file.data['other']     = np.array([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    data_file.data_names        = ['time/s', 'other']
    data_file.set_attributes(['time/s', 'other'], ['t', 'o'])

    # Test 1: Test that can extract data within specified range.
    test1 = data_file.in_data_range('time/s', 3, 7)
    assert np.array_equal(test1.data['time/s'], np.array([3, 4, 5, 6, 7])), f'Time data is not correct for test 1.'
    assert np.array_equal(test1.data['other'], np.array([30, 40, 50, 60, 70])), f'Other data is not correct for test 1.'

    # Test 2: Test that can extract using attribute.
    test2 = data_file.in_data_range('t', 3, 7)
    assert np.array_equal(test2.data['time/s'], np.array([3, 4, 5, 6, 7])), f'Time data is not correct for test 2.'
    assert np.array_equal(test2.data['other'], np.array([30, 40, 50, 60, 70])), f'Other data is not correct for test 2.'

    # Test 3: Test that if range is outside of data, then all data returned
    test3 = data_file.in_data_range('t', 0, 11)
    assert np.array_equal(test3.data['time/s'], np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])), f'Time data is not correct for test 3.'
    assert np.array_equal(test3.data['other'], np.array([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])), f'Other data is not correct for test 3.'

    # Test 4: Test that if provided attribute is not an array, then an error is raised.
    try:
        data_file.in_data_range('xxx', 3, 7)
    except ValueError as e:
        assert 'is not a data_name or common attribute of the Data object.' in str(e), 'Error message is not correct for test 4.'


def test_ECLab_File_cycles():
    # This test ensures that the cycles function works correctly.
    file1 = 'data_files/PAQ (5mM) TBAPF6 (0,1M) DMSO, N2 100 CO2 0, 100mVs-1, -1,86V-1V_C01.txt'
    file1 = ECLab_File(os.path.join(repository_path, file1))

    file1_cycles_1_2 = file1.cycles(1, 2)
    assert len(file1_cycles_1_2.E) == 11417, f'Length of E is not correct for cycles 1-2.'

    file1_out_of_range_cycles = file1.cycles(200)
    assert len(file1_out_of_range_cycles.E) == 0, f'Length of E is not correct for out of range cycles.'

    file2 = 'data_files/ACC-20, 1M Na2SO4, N2 10mlmin-1, CO2 2,5mlmin-1, 2,5rpm_C01.txt'
    file2 = ECLab_File(os.path.join(repository_path, file2))

    file2_cycles_1_2 = file2.cycles(1, 2)
    correct_end_time = datetime.datetime.strptime('07/11/2024 15:41:35.6007', "%m/%d/%Y %H:%M:%S.%f")
    assert file2_cycles_1_2.end_time == correct_end_time, f'End time should be {correct_end_time} for cycles 1-2 but is {file2_cycles_1_2.end_time}.'

# Testing pull requests