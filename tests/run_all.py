from .file_reader import test_reading_ECLab_Files, test_in_time_range

def run_all_tests():
    test_reading_ECLab_Files()
    test_in_time_range()
    print('All tests passed.')