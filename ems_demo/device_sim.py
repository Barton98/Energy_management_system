import requests
import datetime
import time
import random

BASE = "http://localhost:8000"
DEVICE_ID = "PV_SIM"

buffer = []  # bufor store-and-forward

def make_sample(seq):
    ts = datetime.datetime.now(datetime.UTC).isoformat()
    return {
        "device_id": DEVICE_ID,
        "timestamp": ts,
        "seq_no": seq,
        "voltage_v": round(random.uniform(400, 500), 2),
        "current_a": round(random.uniform(2, 5), 2),
        "power_w": round(random.uniform(1000, 2000), 1),
        "temp_c": round(random.uniform(20, 90), 1),
        "status": "OK"
    }

def send(payload):
    try:
        r = requests.post(f"{BASE}/telemetry", json=payload, timeout=2)
        if r.status_code in (200, 201):
            print(f"✅ sent seq {payload['seq_no']}")
            return True
        else:
            print(f"⚠️ server error {r.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("❌ connection failed, buffering...")
        return False

def main():
    seq = 1
    while True:
        sample = make_sample(seq)
        ok = send(sample)
        if not ok:
            buffer.append(sample)
        else:
            if buffer:
                print(f"🔄 resending {len(buffer)} buffered items...")
                try:
                    r = requests.post(f"{BASE}/telemetry/batch", json=buffer, timeout=5)
                    if r.status_code in (200, 201):
                        print("✅ buffer cleared")
                        buffer.clear()
                except:
                    print("❌ batch resend failed")
        seq += 1
        time.sleep(3)

if __name__ == "__main__":
    main()
