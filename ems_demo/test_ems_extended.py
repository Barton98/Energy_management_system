import requests
import datetime
import pytest

BASE = "http://localhost:8000"

def make_sample(seq, temp=25.0, power=1000):
    ts = datetime.datetime.now(datetime.UTC).isoformat()
    return {
        "device_id": "PV_001",
        "timestamp": ts,
        "seq_no": seq,
        "voltage_v": 450.2,
        "current_a": 3.12,
        "power_w": power,
        "temp_c": temp,
        "status": "OK"
    }

def test_valid_telemetry():
    payload = make_sample(1001)
    r = requests.post(f"{BASE}/telemetry", json=payload)
    assert r.status_code in (200,201)

def test_invalid_payload():
    bad = {"device_id": "PV_001", "timestamp": "BAD_TIMESTAMP", "voltage_v": "abc"}
    r = requests.post(f"{BASE}/telemetry", json=bad)
    assert r.status_code in (400,422)

def test_duplicate_seq_no():
    payload = make_sample(2001)
    r1 = requests.post(f"{BASE}/telemetry", json=payload)
    r2 = requests.post(f"{BASE}/telemetry", json=payload)
    assert r1.status_code in (200,201)
    assert r2.status_code in (200,201,409)

def test_store_and_forward_batch():
    batch = [make_sample(3000+i, temp=20+i) for i in range(3)]
    r = requests.post(f"{BASE}/telemetry/batch", json=batch)
    assert r.status_code in (200,201)
    data = r.json()
    assert data.get("processed") == 3

@pytest.mark.parametrize("temp, expect_alert", [
    (25, False),
    (85, True),
])
def test_temperature_alert(temp, expect_alert):
    # Unique device ID to avoid shared state issues
    device_id = f"TEMP_TEST_{temp}_{hash(str(temp)) % 1000}"
    payload = make_sample(4001, temp=temp)
    payload["device_id"] = device_id  # Override device_id
    r = requests.post(f"{BASE}/telemetry", json=payload)
    assert r.status_code in (200,201)
    alerts = requests.get(f"{BASE}/alerts/device/{device_id}").json()
    has_alert = any(a.get("type") == "TEMP_HIGH" for a in alerts)
    assert has_alert == expect_alert
