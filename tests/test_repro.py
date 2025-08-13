import json

def approx(a,b,rel=0.05):
    return abs(a-b) <= rel*abs(b)

def test_summary_numbers():
    d = json.load(open("outputs/summary/lambda_summary.json"))
    s = d["strict"]; e = d["extended"]
    assert s["N"] == 130
    assert e["N"] == 155
    assert approx(s["median_lambda"], 7.21e-8, rel=0.05)
    assert approx(e["median_lambda"], 6.49e-8, rel=0.05)

def test_odr_fit():
    d = json.load(open("outputs/summary/mass_compactness_odr.json"))
    s = d["strict"]; e = d["extended"]
    assert approx(s["slope"], 0.743, rel=0.03)
    assert approx(e["slope"], 0.747, rel=0.03)
