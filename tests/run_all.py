from .file_reader import test_reading_ECLab_Files, test_in_time_range, test_in_data_range, test_ECLab_File_cycles

def run_all_tests():
    test_reading_ECLab_Files()
    test_in_time_range()
    test_in_data_range()
    test_ECLab_File_cycles()
    print('All tests passed.')