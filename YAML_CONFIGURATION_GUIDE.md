# 🔧 YAML Configuration Guide - ADE7880 Component

## ⚠️ CONFIGURATION ERROR FIXED

**Error:** `[i2c_id] is an invalid option for [sensor.ade7880]`

**Root Cause:** Configuration options on wrong YAML level

---

## ✅ CORRECT YAML STRUCTURE

```yaml
# CORRECT: Top-level ade7880 component
ade7880:
  id: ade7880_device
  i2c_id: i2c_id
  address: 56
  update_interval: 60s

# CORRECT: Sensor platform (under sensor:)
sensor:
  - platform: ade7880
    ade7880_id: ade7880_device
    voltage_a:
      name: "Voltage A"
      unit_of_measurement: "V"
    current_a:
      name: "Current A"
      unit_of_measurement: "A"
    power_a:
      name: "Power A"
      unit_of_measurement: "W"
```

---

## ❌ INCORRECT YAML STRUCTURE (Your error)

```yaml
sensor:
  - platform: ade7880
    i2c_id: i2c_id              # ❌ Wrong level!
    address: 56                 # ❌ Wrong level!
    update_interval: 60s        # ❌ Wrong level!
    voltage_a:
      name: Voltage A
```

**These belong in the top-level `ade7880:` block, not in `sensor:`**

---

## 📋 Complete Working Example

```yaml
# I2C Bus Configuration
i2c:
  - id: i2c_id
    sda: GPIO21
    scl: GPIO22
    frequency: 100kHz

# Main ADE7880 Component (Component-level options)
ade7880:
  id: ade7880_main
  i2c_id: i2c_id
  address: 56
  update_interval: 60s

# Sensor Platform (Sensor-specific configuration)
sensor:
  - platform: ade7880
    ade7880_id: ade7880_main  # Link to component
    
    # Phase A
    voltage_a:
      name: "Phase A Voltage"
      unit_of_measurement: "V"
      device_class: voltage
      state_class: measurement
    
    current_a:
      name: "Phase A Current"
      unit_of_measurement: "A"
      device_class: current
      state_class: measurement
    
    power_a:
      name: "Phase A Power"
      unit_of_measurement: "W"
      device_class: power
      state_class: measurement
    
    # Phase B
    voltage_b:
      name: "Phase B Voltage"
    current_b:
      name: "Phase B Current"
    power_b:
      name: "Phase B Power"
    
    # Phase C
    voltage_c:
      name: "Phase C Voltage"
    current_c:
      name: "Phase C Current"
    power_c:
      name: "Phase C Power"

# Optional: Calibration Services
api:
  services:
    - service: calibrate_voltage
      variables:
        phase: string
        target_voltage: float
      then:
        - logger.log:
            format: "Calibrating voltage for phase %s to %.2f V"
            args: ["phase.c_str()", "target_voltage"]
```

---

## 🎯 Quick Fix for Your Config

**Change this:**
```yaml
sensor:
  - platform: ade7880
    i2c_id: i2c_id           # ❌ Move this out
    address: 56              # ❌ Move this out
    update_interval: 60s     # ❌ Move this out
    voltage_a:
      name: Voltage A
```

**To this:**
```yaml
ade7880:
  id: ade7880_device
  i2c_id: i2c_id           # ✅ Here!
  address: 56              # ✅ Here!
  update_interval: 60s     # ✅ Here!

sensor:
  - platform: ade7880
    ade7880_id: ade7880_device  # ✅ Add reference!
    voltage_a:
      name: Voltage A
```

---

## 📊 YAML Structure Summary

| Option | Level | Belongs In |
|--------|-------|-----------|
| `i2c_id` | Component | `ade7880:` block |
| `address` | Component | `ade7880:` block |
| `update_interval` | Component | `ade7880:` block |
| `voltage_a`, `current_a`, etc. | Platform | `sensor:` block with `platform: ade7880` |
| `ade7880_id` | Platform Link | `sensor:` block to reference component |

---

## 🧪 Minimal Test Config

Save as `test_ade7880.yaml`:

```yaml
esphome:
  name: ade7880-test
  platform: esp32
  board: esp32dev

i2c:
  - id: i2c_id
    sda: GPIO21
    scl: GPIO22

ade7880:
  id: ade7880_device
  i2c_id: i2c_id
  address: 56

sensor:
  - platform: ade7880
    ade7880_id: ade7880_device
    voltage_a:
      name: "Voltage A"

external_components:
  - source:
      type: local
      path: ./components/ade7880
    components: [ade7880]
```

Compile with:
```bash
esphome compile test_ade7880.yaml
```

---

## ⚠️ Common Mistakes

1. **Mixing component & platform options**
   - ❌ Putting `i2c_id` under `sensor.ade7880`
   - ✅ Put it in top-level `ade7880:` block

2. **Missing `ade7880_id` in sensor platform**
   - ❌ `platform: ade7880` without linking to component
   - ✅ `platform: ade7880` with `ade7880_id: component_id`

3. **Not defining the component**
   - ❌ Only having `sensor.ade7880` without a top-level `ade7880:` block
   - ✅ Define both component and sensor platform

---

**Status:** ✅ Configuration schema is correct  
**Action Required:** Update your YAML file with correct structure

