from pystil.utils import format_angle


def test_format_angle():
    assert format_angle(121.135) == '121° 8\' 6"'
