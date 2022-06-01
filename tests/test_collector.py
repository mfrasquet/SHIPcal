from shipcal.collectors.collector import FresnelOptics

from pytest import approx, fail
import pytest

@pytest.mark.skip
def test_iam_get():
    optic = FresnelOptics(0.9)
    iams = optic.get_IAM(0,0)
    assert approx(iams[0],1)
    assert approx(iams[1],1)
    assert approx(iams[2],1)
    iams = optic.get_IAM(90,90)
    assert approx(iams[0],0)
    assert approx(iams[1],0)
    assert approx(iams[2],0)
    iams_a = optic.get_IAM(30,30)
    iams_b = optic.get_IAM(27,27)
    assert iams_b[0] > iams_a[0]
    assert iams_b[1] > iams_a[1]
    assert iams_b[2] > iams_a[2]

@pytest.mark.skip
def test_bad_iam():
    demand_iam = "/home/jaarpa/aProjects/solatom/SHIPcal/tests/demand_sin.csv"
    optic = FresnelOptics(0.9, iam_file=demand_iam)
    
