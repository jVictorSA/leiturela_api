import pytest

def test_suite():
    pytest.main(["-v", "--html=report.html"])
