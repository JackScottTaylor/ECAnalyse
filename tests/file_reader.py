import os
import pathlib
import datetime
repository_path = pathlib.Path(__file__).parent.resolve()
data_files_dir = os.path.join(repository_path, 'data_files')

from ..file_reader import ECLab_File

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