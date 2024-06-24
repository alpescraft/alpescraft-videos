import pytest

from logic_v2.tracking import portrait_box_within_bounds_480x810


def test_lower_left():
    assert portrait_box_within_bounds_480x810((0, 0, 200, 200)) == (0, 0, 480, 810)

def test_upper_right():
    assert portrait_box_within_bounds_480x810((1080-200, 1920-200, 200, 200)) == (600, 1110, 480, 810)

def test_upper_left():
    assert portrait_box_within_bounds_480x810((0, 1920-200, 200, 200)) == (0, 1110, 480, 810)

def test_lower_right():
    assert portrait_box_within_bounds_480x810((1080-200, 0, 200, 200)) == (600, 0, 480, 810)

def test_box_within_bounds_should_return_a_box_with_the_same_center():
    centered_in_500x1000 = (250, 500, 500, 1000)
    expected_centered_in_500x1000_scaled_to_480x810 = (500-240, 1000-405, 480, 810)
    assert portrait_box_within_bounds_480x810(centered_in_500x1000) == expected_centered_in_500x1000_scaled_to_480x810

@pytest.mark.skip("not real")
def test_real_example():
    assert portrait_box_within_bounds_480x810((102, 296, 215, 176)) == (82, 386, 480, 810)