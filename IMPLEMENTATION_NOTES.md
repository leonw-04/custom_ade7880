"""
C++ Implementation Details and Technical Notes
ADE7880 ESPHome Custom Component
================================================

This file documents the critical implementation details for the ADE7880
calibration component, including register access patterns, data format
conversions, and calibration mathematics.
"""

# ============================================================================
# 1. I2C COMMUNICATION PROTOCOL
# ============================================================================

## Register Address Format (16-bit Big-Endian)

The ADE7880 expects all register addresses as 2-byte big-endian values.
When transmitting over I2C:

    Register Address 0x43C0 (AIRMS):
    ├─ First Byte (MSB):  0x43
    └─ Second Byte (LSB): 0xC0

Implementation in C++:
```cpp
uint16_t reg = 0x43C0;
uint8_t buffer[2];
buffer[0] = (reg >> 8) & 0xFF;  // Extract MSB (0x43)
buffer[1] = reg & 0xFF;          // Extract LSB (0xC0)
i2c_write(buffer, 2);
```

## Data Transmission Format

### For 32-bit Registers (0x43XX range)

The I2C write sequence is:
```
[Addr_MSB] [Addr_LSB] [Data_MSB] [Data_B1] [Data_B2] [Data_LSB]
  0x43       0xC0      0xXX      0xXX     0xXX      0xXX
```

Example: Write value 0x00ABCDEF to register 0x43C0 (AIRMS)

```cpp
uint16_t reg = 0x43C0;
uint32_t value = 0x00ABCDEF;
uint8_t buffer[6];

// Address bytes (big-endian)
buffer[0] = (reg >> 8) & 0xFF;
buffer[1] = reg & 0xFF;

// Data bytes (big-endian)
buffer[2] = (value >> 24) & 0xFF;
buffer[3] = (value >> 16) & 0xFF;
buffer[4] = (value >> 8) & 0xFF;
buffer[5] = value & 0xFF;

this->write(buffer, 6);
```

### For 16-bit Registers (0xE6XX range)

Only 2 data bytes are transmitted:
```
[Addr_MSB] [Addr_LSB] [Data_MSB] [Data_LSB]
  0xE6       0x04      0xXX      0xXX
```

### For 8-bit Registers

Only 1 data byte is transmitted:
```
[Addr_MSB] [Addr_LSB] [Data_Byte]
  0xE5       0x04      0xXX
```

## Reading from Registers

The I2C read sequence is:
1. Write register address (2 bytes)
2. Read data bytes (4, 2, or 1 bytes depending on register)

```cpp
uint16_t read_register(uint16_t reg, uint8_t bytes) {
  // Write address
  uint8_t addr_buf[2] = {
    (uint8_t)((reg >> 8) & 0xFF),
    (uint8_t)(reg & 0xFF)
  };
  this->write(addr_buf, 2);
  
  // Read data
  uint8_t data_buf[4] = {0};
  this->read(data_buf, bytes);
  
  // Convert to uint32_t (big-endian)
  uint32_t value = 0;
  for (int i = 0; i < bytes; i++) {
    value = (value << 8) | data_buf[i];
  }
  
  return value;
}
```

# ============================================================================
# 2. 24-BIT SIGNED VALUE HANDLING
# ============================================================================

## Problem: Two's Complement Sign Extension

Many ADE7880 registers are internally 24-bit signed but transmitted as 32-bits.
The upper 8 bits must be sign-extended for correct interpretation.

Example: Reading AWATT register

Raw 32-bit value from I2C:
```
Bit position: 31-24  23-16  15-8   7-0
Raw bytes:    0xXX   0xAB   0xCD   0xEF
```

The actual 24-bit value is in bits 23-0:
```
Bits 23-16: 0xAB
Bits 15-8:  0xCD
Bits 7-0:   0xEF
```

### Sign-Extension Algorithm

If bit 23 (the MSB of the 24-bit value) is 1, the value is negative.
We must extend bit 23 into all upper 8 bits (bits 31-24).

```cpp
int32_t convert_24bit_signed(uint32_t raw_value) {
  // Extract lower 24 bits
  int32_t value = raw_value & 0xFFFFFF;
  
  // Check if sign bit (bit 23) is set
  if (value & 0x800000) {
    // Sign-extend: Set bits 31-24 to 1
    value |= 0xFF000000;
  }
  
  return value;
}
```

### Examples

Example 1: Positive value
```
Raw I2C:     0x00123456
Masked 24b:  0x00123456
Sign bit 23: 0 (positive)
Result:      +0x00123456 = +1193046
```

Example 2: Negative value
```
Raw I2C:     0x00EDCBA9
Masked 24b:  0x00EDCBA9
Sign bit 23: 1 (negative, because 0xED & 0x80 != 0)
After OR:    0xFFEDCBA9 (sign-extended to 32-bit)
In decimal:  -1193047
```

# ============================================================================
# 3. CALIBRATION MATHEMATICS
# ============================================================================

## Fundamental Formula

The ADE7880 measurement equation is:

```
Measurement_Output = ADC_Raw_Output × (1 + Gain_Register / 2^23)
```

Where:
- `ADC_Raw_Output` = unkalibrier Messwert aus dem IC
- `Gain_Register` = 24-bit signed Wert (-0x800000 bis +0x7FFFFF)
- `2^23` = 8388608 (Normalisierungsfaktor)

## Deriving the Gain Formula

If we know:
- Measured value (M) = ADC_Raw × (1 + G/2^23)
- Target value (T) = what we want the output to be

Then:
```
T = M × (1 + G/2^23)
T/M = 1 + G/2^23
G/2^23 = (T/M) - 1
G = ((T/M) - 1) × 2^23
```

## Gain Register Value Calculation

```cpp
uint32_t calculate_gain_register(float measured, float target) {
  if (measured == 0) {
    return 0;  // Cannot calibrate with zero
  }
  
  // Ratio calculation
  float ratio = target / measured;
  
  // Gain = ((ratio) - 1) × 2^23
  int32_t gain = (int32_t)((ratio - 1.0f) * 8388608.0f);
  
  // Clamp to 24-bit signed range
  if (gain > 0x7FFFFF)   gain = 0x7FFFFF;
  if (gain < -0x800000)  gain = -0x800000;
  
  return (uint32_t)gain;
}
```

## Examples

### Voltage Calibration Example

Given:
- Measured AVRMS: 225.0 V (Istwert)
- Target voltage: 230.0 V (Sollwert)

Calculation:
```
ratio = 230.0 / 225.0 = 1.02222
gain = (1.02222 - 1.0) × 8388608 = 0.02222 × 8388608 = 186542 (0x2DAAE)
```

After applying this gain:
```
New measurement = 225.0 × (1 + 186542/8388608)
                = 225.0 × (1 + 0.02222)
                = 225.0 × 1.02222
                = 230.0 V ✓
```

### Current Calibration Example

Given:
- Measured AIRMS: 9.8 A (Istwert)
- Target current: 10.0 A (Sollwert)

Calculation:
```
ratio = 10.0 / 9.8 = 1.0204
gain = (1.0204 - 1.0) × 8388608 = 0.0204 × 8388608 = 171163 (0x29D4B)
```

### Power Calibration Example

Given:
- Measured AWATT: 1950 W (Istwert, unsigned interpretation)
- Target power: 2000 W (Sollwert)

Calculation:
```
ratio = 2000 / 1950 = 1.0256
gain = (1.0256 - 1.0) × 8388608 = 0.0256 × 8388608 = 214991 (0x3460F)
```

# ============================================================================
# 4. PERSISTENT STORAGE IMPLEMENTATION
# ============================================================================

## CalibrationData Structure

```cpp
struct CalibrationData {
  int32_t aigain;  // Phase A current gain
  int32_t avgain;  // Phase A voltage gain
  int32_t apgain;  // Phase A power gain
  
  int32_t bigain;  // Phase B current gain
  int32_t bvgain;  // Phase B voltage gain
  int32_t bpgain;  // Phase B power gain
  
  int32_t cigain;  // Phase C current gain
  int32_t cvgain;  // Phase C voltage gain
  int32_t cpgain;  // Phase C power gain
};
```

Total size: 9 × 4 bytes = 36 bytes
With CRC8: ~40 bytes in Flash

## ESPPreferences API Usage

```cpp
void load_calibration_from_flash_() {
  // Create a preference with CRC protection
  auto calib_pref = global_preferences->make_preference<CalibrationData>(
      0x44415E37,           // Namespace ID (arbitrary)
      crc8("ade7880_calib")  // Key hash
  );
  
  // Try to load stored data
  if (calib_pref.load(&calibration_data_)) {
    ESP_LOGI(TAG, "Calibration data loaded from Flash");
  } else {
    // No data stored or corrupted, use defaults
    ESP_LOGI(TAG, "No calibration data found, using defaults");
    calibration_data_ = CalibrationData();  // All zeros
  }
}

void save_calibration_to_flash_() {
  auto calib_pref = global_preferences->make_preference<CalibrationData>(
      0x44415E37,
      crc8("ade7880_calib")
  );
  
  if (calib_pref.save(&calibration_data_)) {
    ESP_LOGI(TAG, "Calibration data saved to Flash");
  } else {
    ESP_LOGE(TAG, "Failed to save calibration data");
  }
}
```

## Flash Persistence Guarantees

- **Survival:** Persists across reboots and OTA updates
- **Integrity:** CRC8 checksum protects against corruption
- **Atomicity:** ESPPreferences handles atomic writes
- **Durability:** Stored in NVS partition (typically 16 KB reserved)

# ============================================================================
# 5. REGISTER ADDRESS REFERENCE
# ============================================================================

## Measurement Registers (Read-Only, 4 Bytes)

| Name  | Address | Format | Scaling |
|-------|---------|--------|---------|
| AIRMS | 0x43C0  | u32    | × 0.0001 |
| AVRMS | 0x43C1  | u32    | × 0.001 |
| BIRMS | 0x43C2  | u32    | × 0.0001 |
| BVRMS | 0x43C3  | u32    | × 0.001 |
| CIRMS | 0x43C4  | u32    | × 0.0001 |
| CVRMS | 0x43C5  | u32    | × 0.001 |
| AWATT | 0x43A8  | i32*   | × 0.01 |
| BWATT | 0x43A9  | i32*   | × 0.01 |
| CWATT | 0x43AA  | i32*   | × 0.01 |

*Note: 24-bit signed, requires sign-extension from 32-bit read

## Gain Registers (Read/Write, 4 Bytes)

| Name  | Address | Phase | Purpose |
|-------|---------|-------|---------|
| AIGAIN| 0x4380  | A     | Current correction |
| AVGAIN| 0x4381  | A     | Voltage correction |
| APGAIN| 0x4382  | A     | Power correction |
| BIGAIN| 0x4383  | B     | Current correction |
| BVGAIN| 0x4384  | B     | Voltage correction |
| BPGAIN| 0x4385  | B     | Power correction |
| CIGAIN| 0x4386  | C     | Current correction |
| CVGAIN| 0x4387  | C     | Voltage correction |
| CPGAIN| 0x4388  | C     | Power correction |

All gain registers:
- **Format:** 24-bit signed two's complement (extended to 32-bit on I2C)
- **Range:** -0x800000 (-2,097,152) to +0x7FFFFF (+2,097,151)
- **Default:** 0x000000 (no correction)

# ============================================================================
# 6. HOME ASSISTANT CUSTOM API SERVICES
# ============================================================================

## Service Registration

```cpp
// In setup() method
register_service<std::string, float>(
    &ADE7880Component::calibrate_voltage,
    "calibrate_voltage",
    {"phase", "target_voltage"}
);
```

## Service Call Example (YAML in HA)

```yaml
service: ade7880.calibrate_voltage
data:
  phase: "A"
  target_voltage: 230.5
```

## Service Implementation Pattern

```cpp
void ADE7880Component::calibrate_voltage(std::string phase, 
                                         float target_voltage) {
  // 1. Parse phase ("A", "B", "C")
  uint16_t phase_idx = get_phase_index(phase);
  
  // 2. Get register addresses for this phase
  PhaseRegisters regs = get_phase_registers(phase_idx);
  
  // 3. Read current (uncalibrated) measurement
  uint32_t raw = read_register(regs.vrms, 4);
  float measured = (float)raw * 0.001f;
  
  // 4. Calculate gain correction
  uint32_t gain = calculate_gain_register(measured, target_voltage);
  
  // 5. Write gain to device
  write_register(regs.vgain, gain, 4);
  
  // 6. Update in-memory struct
  calibration_data_.avgain = (int32_t)gain;  // Or bvgain, cvgain...
  
  // 7. Save to Flash
  save_calibration_to_flash_();
  
  ESP_LOGI(TAG, "Calibration complete for phase %s", phase.c_str());
}
```

# ============================================================================
# 7. TROUBLESHOOTING GUIDE
# ============================================================================

## Issue: I2C Communication Fails

**Symptoms:**
```
[i2c] I2C bus (0x0) register read failed for device at 0x38
```

**Root Causes:**
1. Incorrect GPIO pins (check CONFIG_I2C_SDA_GPIO / CONFIG_I2C_SCL_GPIO)
2. Missing pull-up resistors (need 4.7 kΩ from SDA/SCL to 3.3V)
3. Device not powered
4. Address mismatch (device not at 0x38)

**Solution:**
```yaml
i2c:
  sda: GPIO21     # ← Verify these pins
  scl: GPIO22
  frequency: 100kHz  # ← Try lower frequency
  scan: true      # ← Enable to find actual address
```

## Issue: Calibration Values Not Persisting

**Symptoms:**
- Calibration works, but after reboot: gains are reset to 0

**Root Causes:**
1. ESPPreferences storage not initialized
2. Insufficient Flash space
3. NVS partition corrupted

**Solution:**
```yaml
# In esphome configuration
logger:
  level: DEBUG
  logs:
    ade7880: DEBUG
```

Monitor logs for "Calibration data saved to Flash" and "Calibration data loaded from Flash".

## Issue: Gain Calculation Results in 0

**Symptoms:**
```
[ade7880] Measured voltage for phase A: 0.000 V
[ade7880] Measured voltage too low or zero, calibration aborted
```

**Root Causes:**
1. ADE7880 not properly initialized
2. Measurement register address incorrect
3. I2C data not being read correctly

**Solution:**
- Verify ADE7880 firmware version and initialization sequence
- Check register addresses against datasheet
- Increase I2C frequency back to 100-200 kHz for better SNR

# ============================================================================
# 8. PERFORMANCE CONSIDERATIONS
# ============================================================================

## Update Interval

Recommended: 60 seconds
- Allows ADE7880 to accumulate line-cycle measurements
- Sufficient for Home Assistant state updates
- Balances responsiveness with I2C bus load

```yaml
update_interval: 60s
```

## I2C Frequency

Recommended: 100 kHz (conservative)
- ADE7880 supports up to 400 kHz
- Lower frequency = more reliable over longer cables
- Conservative choice for production systems

## Calibration Speed

- Single calibration: ~100 ms (register write + Flash save)
- Total boot time impact: ~1 second (load from Flash + apply to 9 registers)

# ============================================================================
# 9. VALIDATION CHECKLIST
# ============================================================================

Before deployment:

- [ ] I2C communication verified (scan finds device at 0x38)
- [ ] Sensor readings within expected range (230V, 10A, 2kW)
- [ ] Calibration service callable from Home Assistant
- [ ] Gain values correctly calculated and applied
- [ ] Data persists after reboot
- [ ] Reset service works correctly
- [ ] No memory leaks (check IRAM/DRAM usage over 24h)
- [ ] Log messages are clear and helpful

---

**Document Version:** 1.0
**Last Updated:** 2026-06-25
"""
