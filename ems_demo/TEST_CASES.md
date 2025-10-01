# 🧪 MANUAL TEST CASES - EMS API

## 📋 **POSITIVE TEST CASES**

### **TC001: Valid telemetry data**
**Scenario:** Send valid telemetry data to API  
**Steps:**
1. Open Postman
2. Send POST to `/telemetry` with valid JSON:
   ```json
   {
     "device_id": "PV_001",
     "timestamp": "2024-01-01T10:00:00Z",
     "seq_no": 1,
     "temp_c": 25.0,
     "voltage_v": 12.5
   }
   ```
3. Check response

**Expected Result:** 
- Status: 200 OK
- Response: `{"result": "ok"}`
- No alerts generated (temp < 80°C)

**Actual Result:** [TO BE FILLED DURING TESTING]

---

### **TC002: Temperature alert generation**
**Scenario:** High temperature should generate alert  
**Steps:**
1. Send POST to `/telemetry` with high temperature:
   ```json
   {
     "device_id": "PV_002", 
     "timestamp": "2024-01-01T11:00:00Z",
     "seq_no": 2,
     "temp_c": 85.0
   }
   ```
2. Check immediate response
3. GET `/alerts/device/PV_002` to verify alert stored

**Expected Result:**
- Status: 200 OK  
- Alert created with temp > 80°C
- Alert visible in alerts endpoint

---

## ❌ **NEGATIVE TEST CASES**

### **TC003: Invalid data type**
**Scenario:** API should reject invalid data types  
**Steps:**
1. Send POST with string instead of number:
   ```json
   {
     "device_id": "PV_003",
     "temp_c": "hot"
   }
   ```

**Expected Result:** 
- Status: 422 Validation Error
- Clear error message about data type

---

### **TC004: Missing required fields**
**Scenario:** API should reject incomplete data  
**Steps:**
1. Send POST without required field:
   ```json
   {
     "temp_c": 25.0
   }
   ```

**Expected Result:**
- Status: 422 Validation Error  
- Error about missing device_id

---

## 🔄 **EDGE CASES**

### **TC005: Boundary temperature values**
**Scenario:** Test exact alert threshold  
**Test Data:**
- temp_c: 79.9 (should NOT alert)
- temp_c: 80.0 (should alert)  
- temp_c: 80.1 (should alert)

### **TC006: Large batch processing** 
**Scenario:** Test system under load
**Steps:**
1. Send batch with 100+ telemetry items
2. Verify all processed correctly
3. Check response time < 2 seconds

### **TC007: Special characters in device_id**
**Test Data:**
- device_id: "PV-001_test"
- device_id: "PV@001" 
- device_id: "PV 001"

---

## 🌐 **INTEGRATION TEST SCENARIOS**

### **TC008: Device simulator integration**
**Scenario:** Full end-to-end workflow
**Steps:**
1. Start API server
2. Start device simulator  
3. Let run for 2 minutes
4. Verify data appears in telemetry_db
5. Check if any alerts generated

### **TC009: Network failure simulation**
**Scenario:** Test store-and-forward mechanism
**Steps:**
1. Start simulator
2. Stop API server (simulate network down)
3. Wait 30 seconds  
4. Restart API server
5. Verify buffered data is sent via batch endpoint

---

## 📊 **PERFORMANCE TEST CASES**

### **TC010: Response time validation**
**Scenario:** API should respond quickly  
**Acceptance Criteria:** < 100ms for single telemetry

### **TC011: Concurrent requests**
**Scenario:** Multiple devices sending simultaneously
**Steps:** Send 10 requests in parallel, verify all processed

---

## 🔒 **SECURITY TEST CASES**

### **TC012: SQL Injection attempt**  
**Test Data:** Try malicious device_id values

### **TC013: Oversized payload**
**Test Data:** Send very large JSON (>1MB)

---

## 📝 **TEST EXECUTION CHECKLIST**

**Pre-conditions:**
- [ ] API server running on localhost:8000
- [ ] Postman collection imported  
- [ ] Test data prepared

**Post-conditions:**
- [ ] All test results documented
- [ ] Bugs reported in tracking system
- [ ] Test environment cleaned up