import pytest
import numpy as np
import datetime
from ECAnalyse.Data import Data
from ECAnalyse.Data.Data import TIME_PLACEHOLDER

@pytest.fixture
def sample_data():
    t = np.linspace(0, 10, 11)
    s1 = np.sin(t)
    d = Data()
    d.data = {'Time': t, 'Signal': s1}
    d.t_data_name = 'Time'
    d.start_time = datetime.datetime(2023, 1, 1, 0, 0)
    d.time_format = "%Y-%m-%d %H:%M:%S"
    return d

def test_data_names(sample_data):
    assert set(sample_data.data_names) == {'Time', 'Signal'}

def test_set_start_time_and_shift_end_time(sample_data):
    original_duration = sample_data.end_time - sample_data.start_time
    new_start = datetime.datetime(2025, 1, 1, 12, 0)
    sample_data.set_start_time(new_start)
    assert sample_data.start_time == new_start
    assert sample_data.end_time - sample_data.start_time == original_duration

def test_set_end_time_and_shift_start_time(sample_data):
    original_duration = sample_data.end_time - sample_data.start_time
    new_end = datetime.datetime(2026, 1, 1, 12, 0)
    sample_data.set_end_time(new_end)
    assert sample_data.end_time == new_end
    assert sample_data.end_time - sample_data.start_time == original_duration

def test_in_data_range(sample_data):
    filtered = sample_data.in_data_range('Signal', -0.5, 0.5)
    assert np.all(
        (filtered.data['Signal'] >= -0.5) & (filtered.data['Signal'] <= 0.5)
        )

def test_in_time_range_with_datetime(sample_data):
    start = sample_data.start_time + datetime.timedelta(seconds=3)
    end   = sample_data.start_time + datetime.timedelta(seconds=7)
    filtered = sample_data.in_time_range(start, end)
    assert np.all(filtered.data['Time'] >= 3)
    assert np.all(filtered.data['Time'] <= 7)

def test_zero_time_adjusts_timestamps(sample_data):
    original_start = sample_data.start_time
    delta = sample_data.data['Time'][0]
    sample_data.zero_time()
    assert sample_data.data['Time'][0] == 0
    assert sample_data.start_time == original_start - datetime.timedelta(
                                                                seconds=delta)

def test_data_key_lookup(sample_data):
    sample_data.set_attributes(['Signal'], ['s'])
    assert sample_data.data_key('Signal') == 'Signal'
    assert sample_data.data_key('s') == 'Signal'
    with pytest.raises(ValueError):
        sample_data.data_key('nonexistent')

def test_rolling_average_single(sample_data):
    avg = sample_data.rolling_average('Signal', w=3)
    expected = np.convolve(
        sample_data.data['Signal'], np.ones(3)/3, mode='valid')
    np.testing.assert_allclose(avg, expected)

def test_addition_merges_data():
    t = np.linspace(0, 10, 11)
    s = np.sin(t)
    d1 = Data()
    d2 = Data()
    for d in (d1, d2):
        d.data = {'Time': t, 'Signal': s}
        d.t_data_name = 'Time'
        d.start_time = datetime.datetime(2023, 1, 1, 0, 0)
    d_combined = d1 + d2
    assert len(d_combined.data['Signal']) == 22
    assert len(d_combined.data['Time']) == 22



