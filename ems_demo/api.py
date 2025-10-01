from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn

app = FastAPI()

telemetry_db: List[Dict] = []
alerts_db: Dict[str, List[Dict]] = {}

# model danych telemetry
class Telemetry(BaseModel):
    device_id: str
    timestamp: str
    seq_no: int
    voltage_v: Optional[float] = None
    current_a: Optional[float] = None
    power_w: Optional[float] = None
    temp_c: Optional[float] = None
    status: str = "OK"

@app.post("/telemetry")
def receive_telemetry(data: Telemetry):
    telemetry_db.append(data.model_dump())
    
    # Current: Single threshold alert system (>80°C)
    # TODO: Multi-level alerts (WARNING/CRITICAL/EMERGENCY) - details in README.md
    if data.temp_c and data.temp_c > 80:
        alerts_db.setdefault(data.device_id, []).append({
            "type": "TEMP_HIGH",
            "value": data.temp_c,
            "timestamp": data.timestamp
        })
    return {"result": "ok"}

@app.post("/telemetry/batch")
def receive_batch(batch: List[Telemetry]):
    for item in batch:
        telemetry_db.append(item.model_dump())
        if item.temp_c and item.temp_c > 80:
            alerts_db.setdefault(item.device_id, []).append({
                "type": "TEMP_HIGH",
                "value": item.temp_c,
                "timestamp": item.timestamp
            })
    return {"processed": len(batch)}

@app.get("/alerts/device/{device_id}")
def get_alerts(device_id: str):
    return alerts_db.get(device_id, [])

@app.get("/health")
def health_check():
    return {"status": "healthy", "telemetry_count": len(telemetry_db), "alerts_count": sum(len(alerts) for alerts in alerts_db.values())}

if __name__ == "__main__":
    print("Starting EMS API server on http://0.0.0.0:8000")
    print("Press CTRL+C to stop the server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
