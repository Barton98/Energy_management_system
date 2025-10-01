# 📝 Przykłady danych dla EMS API

Ten folder zawiera przykładowe dane JSON do testowania i demonstracji API Energy Management System.

## 🔧 Jak używać podczas prezentacji

### 1. Uruchom API server
```bash
python api.py
```

### 2. Testuj endpointy z przykładowymi danymi

#### Normalne dane telemetryczne
```powershell
$json = Get-Content examples/telemetry_normal.json -Raw
Invoke-RestMethod -Uri "http://localhost:8000/telemetry" -Method Post -Body $json -ContentType "application/json"
```

#### Dane z alertem (temperatura >80°C)
```powershell
$json = Get-Content examples/telemetry_alert.json -Raw
Invoke-RestMethod -Uri "http://localhost:8000/telemetry" -Method Post -Body $json -ContentType "application/json"
```

#### Batch processing (3 urządzenia, 1 alert)
```powershell
$json = Get-Content examples/batch_data.json -Raw
Invoke-RestMethod -Uri "http://localhost:8000/telemetry/batch" -Method Post -Body $json -ContentType "application/json"
```

### 3. Sprawdź wyniki

#### Status systemu
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
```

#### Alerty dla konkretnego urządzenia
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/alerts/device/test-device-01" -Method Get
```

## 📊 Zawartość plików

- **`telemetry_normal.json`**: Normalne dane z temp=45.5°C (bez alertu)
- **`telemetry_alert.json`**: Dane z temp=85.2°C (wywołuje alert TEMP_HIGH)
- **`batch_data.json`**: 3 urządzenia wsadowo, jedno z alertem temp=82.5°C

## 🎯 Scenariusz demo dla rekrutera

1. Pokaż normalny przepływ danych
2. Zademonstruj system alertów
3. Pokaż przetwarzanie wsadowe
4. Sprawdź statystyki i alerty