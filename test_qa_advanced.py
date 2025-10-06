# � MID-LEVEL QA AUTOMATED TESTS 

import requests
import datetime  
import pytest
import time

BASE = "http://localhost:8000"

# Podstawowe dane testowe - proste i zrozumiałe
def create_test_telemetry(device_id="TEST_001", temp=25.0, seq=1):
    """Tworzy dane testowe - łatwe do modyfikacji"""
    return {
        "device_id": device_id, 
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "seq_no": seq,
        "voltage_v": 12.5,
        "current_a": 8.2, 
        "power_w": 102.5,
        "temp_c": temp,
        "status": "OK"
    }

# ✅ PODSTAWOWE TESTY FUNKCJONALNE - MID LEVEL

def test_api_is_running():
    """Sprawdź czy API w ogóle działa"""
    try:
        response = requests.get(f"{BASE}/docs")
        assert response.status_code == 200
        print("✅ API is running")
    except requests.exceptions.ConnectionError:
        pytest.fail("❌ API server nie działa. Uruchom: python api.py")

def test_send_valid_telemetry():
    """Test podstawowy - wyślij poprawne dane"""
    data = create_test_telemetry()
    
    response = requests.post(f"{BASE}/telemetry", json=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["result"] == "ok"
    print(f"✅ Telemetry sent for device {data['device_id']}")

def test_missing_device_id():
    """Test - brak wymaganego pola device_id"""
    bad_data = {
        "temp_c": 25.0,
        "seq_no": 1
        # Brak device_id!
    }
    
    response = requests.post(f"{BASE}/telemetry", json=bad_data)
    
    assert response.status_code == 422  # Validation error
    print("✅ API correctly rejected data without device_id")

def test_wrong_data_types():
    """Test - złe typy danych"""
    bad_data = {
        "device_id": "TEST_001",
        "temp_c": "very hot",  # String zamiast liczby
        "seq_no": 1
    }
    
    response = requests.post(f"{BASE}/telemetry", json=bad_data)
    
    assert response.status_code == 422
    print("✅ API correctly rejected invalid data type")

# 🚨 TESTY ALERTÓW - PROSTE ALE SKUTECZNE

def test_no_alert_for_normal_temperature():
    """Test - normalna temperatura nie powinna generować alertu"""
    data = create_test_telemetry(device_id="NORMAL_TEMP", temp=50.0)
    
    response = requests.post(f"{BASE}/telemetry", json=data)
    assert response.status_code == 200
    
    # Sprawdź czy nie ma alertów
    alerts_response = requests.get(f"{BASE}/alerts/device/NORMAL_TEMP")
    alerts = alerts_response.json()
    assert len(alerts) == 0
    print("✅ Normal temperature - no alerts generated")

def test_high_temperature_creates_alert():
    """Test - wysoka temperatura powinna wygenerować alert"""
    data = create_test_telemetry(device_id="HOT_DEVICE", temp=85.0)
    
    response = requests.post(f"{BASE}/telemetry", json=data)
    assert response.status_code == 200
    
    # Sprawdź czy alert został utworzony
    alerts_response = requests.get(f"{BASE}/alerts/device/HOT_DEVICE")
    alerts = alerts_response.json()
    
    assert len(alerts) > 0, "Expected alert for high temperature"
    alert = alerts[0]
    assert alert["type"] == "TEMP_HIGH"
    assert alert["value"] == 85.0
    print("✅ High temperature alert generated correctly")

def test_alert_threshold_boundary():
    """Test - sprawdź dokładny próg alertów (80°C)"""
    # Temperatura poniżej progu - brak alertu
    data_below = create_test_telemetry(device_id="BELOW_THRESH", temp=79.9)
    response = requests.post(f"{BASE}/telemetry", json=data_below)
    assert response.status_code == 200
    
    alerts_below = requests.get(f"{BASE}/alerts/device/BELOW_THRESH").json()
    assert len(alerts_below) == 0, "Should not alert for 79.9°C"
    
    # Temperatura powyżej progu - alert
    data_above = create_test_telemetry(device_id="ABOVE_THRESH", temp=80.1)  
    response = requests.post(f"{BASE}/telemetry", json=data_above)
    assert response.status_code == 200
    
    alerts_above = requests.get(f"{BASE}/alerts/device/ABOVE_THRESH").json()
    assert len(alerts_above) > 0, "Should alert for 80.1°C"
    
    print("✅ Alert threshold (80°C) works correctly")

# 📦 TESTY BATCH - REALISTYCZNE NA MID LEVEL

def test_empty_batch():
    """Test - pusta lista batch powinna być obsłużona"""
    response = requests.post(f"{BASE}/telemetry/batch", json=[])
    
    assert response.status_code == 200
    result = response.json() 
    assert result["processed"] == 0
    print("✅ Empty batch handled correctly")

def test_small_batch():
    """Test - mały batch (3 elementy)"""
    batch_data = [
        create_test_telemetry("BATCH_1", temp=25.0, seq=1),
        create_test_telemetry("BATCH_2", temp=50.0, seq=2), 
        create_test_telemetry("BATCH_3", temp=85.0, seq=3)  # Ten powinien wygenerować alert
    ]
    
    response = requests.post(f"{BASE}/telemetry/batch", json=batch_data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["processed"] == 3
    
    # Sprawdź czy alert został wygenerowany dla gorącego urządzenia
    alerts = requests.get(f"{BASE}/alerts/device/BATCH_3").json()
    assert len(alerts) > 0, "Expected alert for device with 85°C"
    
    print("✅ Small batch processed with alerts")

def test_batch_performance():
    """Test - sprawdź czy batch nie jest za wolny"""
    # Przygotuj 10 elementów
    batch_data = []
    for i in range(10):
        batch_data.append(create_test_telemetry(f"PERF_{i}", temp=30.0, seq=i))
    
    start_time = time.time()
    response = requests.post(f"{BASE}/telemetry/batch", json=batch_data)
    end_time = time.time()
    
    processing_time = end_time - start_time
    
    assert response.status_code == 200
    assert processing_time < 5.0, f"Batch took {processing_time:.2f}s, should be < 5s"
    print(f"✅ Batch of 10 items processed in {processing_time:.3f}s")

# ⚡ PODSTAWOWE TESTY WYDAJNOŚCI

def test_response_time():
    """Test - API powinno odpowiadać szybko"""
    data = create_test_telemetry()
    
    start_time = time.time()
    response = requests.post(f"{BASE}/telemetry", json=data)
    response_time = time.time() - start_time
    
    assert response.status_code == 200
    assert response_time < 3.0, f"Response time {response_time:.3f}s is too slow"
    print(f"✅ Response time: {response_time:.3f}s (good)")

def test_multiple_requests():
    """Test - wyślij kilka requestów po sobie"""
    success_count = 0
    
    for i in range(5):
        data = create_test_telemetry(f"MULTI_{i}", temp=30.0, seq=i)
        response = requests.post(f"{BASE}/telemetry", json=data)
        
        if response.status_code == 200:
            success_count += 1
        
        time.sleep(0.1)  # Krótka przerwa między requestami
    
    assert success_count == 5, f"Only {success_count}/5 requests succeeded"
    print("✅ Multiple sequential requests handled correctly")

# 🔗 PROSTE TESTY INTEGRACYJNE  

def test_device_lifecycle():
    """Test - symuluj życie urządzenia: start → normalna praca → przegrzanie"""
    device_id = "LIFECYCLE_DEVICE"
    
    # 1. Urządzenie się uruchamia
    startup_data = create_test_telemetry(device_id, temp=20.0, seq=1)
    response = requests.post(f"{BASE}/telemetry", json=startup_data)
    assert response.status_code == 200
    print("✅ Device startup - OK")
    
    # 2. Normalna praca (kilka pomiarów)
    for i in range(2, 5):
        normal_temp = 25.0 + (i * 5)  # Powoli rośnie temperatura
        normal_data = create_test_telemetry(device_id, temp=normal_temp, seq=i)
        response = requests.post(f"{BASE}/telemetry", json=normal_data)
        assert response.status_code == 200
    
    print("✅ Normal operation - OK")
    
    # 3. Przegrzanie - powinien być alert
    overheat_data = create_test_telemetry(device_id, temp=85.0, seq=5)
    response = requests.post(f"{BASE}/telemetry", json=overheat_data)
    assert response.status_code == 200
    
    # Sprawdź czy alert został wygenerowany
    alerts = requests.get(f"{BASE}/alerts/device/{device_id}").json()
    assert len(alerts) > 0, "Expected alert for overheating device"
    
    print("✅ Overheating alert generated - OK")
    print("✅ Complete device lifecycle test passed")

def test_api_endpoints_exist():
    """Test - sprawdź czy wszystkie endpointy istnieją"""
    # Test dokumentacji
    docs_response = requests.get(f"{BASE}/docs")
    assert docs_response.status_code == 200
    print("✅ /docs endpoint works")
    
    # Test OpenAPI spec
    openapi_response = requests.get(f"{BASE}/openapi.json")
    assert openapi_response.status_code == 200
    spec = openapi_response.json()
    
    # Sprawdź czy endpointy są w specyfikacji
    assert "/telemetry" in spec["paths"]
    assert "/telemetry/batch" in spec["paths"] 
    assert "/alerts/device/{device_id}" in spec["paths"]
    
    print("✅ All expected endpoints found in API spec")