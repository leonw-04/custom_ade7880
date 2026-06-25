# 🏗️ ADE7880 Component Architecture - Final (ESPHome 2025+)

## Architecture Overview

The ADE7880 component for ESPHome 2025+ follows a **simplified, single-configuration model**:

### Components Structure

```
components/ade7880/
├── __init__.py                   ← Main component + all sensor definitions
├── sensor.py                     ← Documentation stub (no functional code)
├── ade7880_calibration.h         ← C++ header
└── ade7880_calibration.cpp       ← C++ implementation
```

## Configuration Flow

### 1. ESPHome Config Parsing (`YAML`)

```yaml
ade7880:
  id: ade7880_device
  i2c_id: i2c_id
  address: 56
  update_interval: 60s
  
  voltage_a:
    name: "Phase A Voltage"
  current_a:
    name: "Phase A Current"
  power_a:
    name: "Phase A Power"
  
  # ... 6 more sensors (phases B & C)
```

### 2. Python Configuration Validation (`__init__.py`)

```python
CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(ADE7880Component),
    
    # Sensor definitions (all 9)
    cv.Optional(CONF_VOLTAGE_A): sensor.sensor_schema(
        unit_of_measurement=UNIT_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        ...
    ),
    cv.Optional(CONF_CURRENT_A): sensor.sensor_schema(...),
    cv.Optional(CONF_POWER_A): sensor.sensor_schema(...),
    # ... B and C phases
    
}).extend(cv.polling_component_schema("60s")).extend(
    i2c.i2c_device_schema(0x38)
)
```

### 3. C++ Code Generation (`to_code()`)

```python
async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await i2c.register_i2c_device(var, config)
    
    # Create and link all sensors
    if CONF_VOLTAGE_A in config:
        sens = await sensor.new_sensor(config[CONF_VOLTAGE_A])
        cg.add(var.set_voltage_sensor_a(sens))
    
    # ... repeat for all 9 sensors
```

### 4. C++ Component Execution

```cpp
class ADE7880Component : public PollingComponent, public i2c::I2CDevice {
    void setup() {
        // Initialize I2C, load calibration from Flash
    }
    
    void update() {
        // Read 9 measurements
        // Update sensor values
    }
};
```

## Key Design Decisions

### ✅ Single Config vs Separate Platforms

**Wrong** (what we initially tried):
```yaml
ade7880:
  id: ade7880_device
  i2c_id: i2c_id

sensor:
  - platform: ade7880
    ade7880_id: ade7880_device  # ❌ Creates second validation scope
    voltage_a: ...
```

**Correct** (current implementation):
```yaml
ade7880:
  id: ade7880_device
  i2c_id: i2c_id
  voltage_a: ...                # ✅ Single validation scope
```

### Why?

ESPHome's CONFIG_SCHEMA validation is hierarchical:
- `ade7880:` block uses `__init__.py` CONFIG_SCHEMA
- `sensor: - platform: ade7880:` would use a SEPARATE schema validation
- Creating `sensor.ade7880` platform without explicit schema handling causes conflicts

**Solution**: Keep everything in one CONFIG_SCHEMA in `__init__.py`

### sensor.py Purpose

In ESPHome 2025+:
- `__init__.py` = component definition + configuration
- `sensor.py` = optional; only needed for **separate sensor platforms**

For ADE7880:
- All sensors are part of the component
- `sensor.py` is a documentation stub (kept for compatibility)
- No separate sensor platform logic needed

## Configuration Schema Hierarchy

```
CONFIG_SCHEMA (in __init__.py)
├── GenerateID (ade7880_device)
├── I2C options (via i2c.i2c_device_schema(0x38))
│   ├── i2c_id
│   ├── address (0x38)
│   └── ... other I2C options
├── Polling options (via cv.polling_component_schema("60s"))
│   ├── update_interval (default 60s)
│   └── ... other polling options
└── Sensor definitions
    ├── voltage_a (sensor_schema)
    ├── voltage_b (sensor_schema)
    ├── voltage_c (sensor_schema)
    ├── current_a (sensor_schema)
    ├── current_b (sensor_schema)
    ├── current_c (sensor_schema)
    ├── power_a (sensor_schema)
    ├── power_b (sensor_schema)
    └── power_c (sensor_schema)
```

## Data Flow During Compilation

```
1. YAML Parsing
   └─> ESPHome reads ade7880: block

2. Schema Validation
   └─> __init__.py CONFIG_SCHEMA validates all options

3. Python Code Generation (to_code)
   ├─> Creates ADE7880Component instance
   ├─> Registers as PollingComponent
   ├─> Registers with I2C bus
   └─> Creates 9 sensor objects and links them

4. C++ Code Generation
   └─> Generates C++ class instances

5. Compilation
   └─> Firmware ready to flash
```

## YAML Configuration Examples

### Minimal (only Phase A)

```yaml
ade7880:
  id: ade7880_device
  i2c_id: i2c_id
  voltage_a:
    name: "Voltage A"
  current_a:
    name: "Current A"
  power_a:
    name: "Power A"
```

### Full (all 3 phases, all sensors)

```yaml
ade7880:
  id: ade7880_device
  i2c_id: i2c_id
  address: 56
  update_interval: 60s
  
  # Phase A
  voltage_a:
    name: "Phase A Voltage"
    unit_of_measurement: "V"
  current_a:
    name: "Phase A Current"
    unit_of_measurement: "A"
  power_a:
    name: "Phase A Power"
    unit_of_measurement: "W"
  
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
```

## C++ Class Structure

```cpp
namespace esphome::ade7880 {

class ADE7880Component : public PollingComponent, public i2c::I2CDevice {
 public:
  void setup() override;
  void update() override;
  void dump_config() override;
  
  // Sensor setters (called during to_code)
  void set_voltage_sensor_a(sensor::Sensor *sensor);
  void set_current_sensor_a(sensor::Sensor *sensor);
  void set_power_sensor_a(sensor::Sensor *sensor);
  // ... B and C phases
  
 private:
  sensor::Sensor *voltage_sensor_a_ = nullptr;
  sensor::Sensor *current_sensor_a_ = nullptr;
  sensor::Sensor *power_sensor_a_ = nullptr;
  // ... B and C phases
  
  // Calibration methods
  void calibrate_voltage(const std::string &phase, float target_voltage);
  void calibrate_current(const std::string &phase, float target_current);
  void calibrate_power(const std::string &phase, float target_power);
  void reset_calibration();
  
  // I2C register I/O
  uint32_t read_register(uint16_t reg, uint8_t bytes);
  void write_register(uint16_t reg, uint32_t value, uint8_t bytes);
  
  // Persistence
  CalibrationData load_calibration();
  void save_calibration(const CalibrationData &data);
};

} // namespace esphome::ade7880
```

## Testing the Architecture

### Step 1: Validate Schema

```bash
esphome config config.yaml
# Should show no errors
# Should list all 9 sensors if defined
```

### Step 2: Compile

```bash
esphome compile config.yaml
# Should complete without schema errors
# Should generate C++ code
```

### Step 3: Upload & Verify

```bash
esphome run config.yaml
# Should upload firmware
# Should see sensor readings in logs
```

## Common Mistakes (Now Fixed)

❌ **Mistake 1**: Separate `sensor:` block with `ade7880_id`
- Causes: `[ade7880_id] is invalid option for sensor.ade7880`
- Fix: Put all in `ade7880:` block

❌ **Mistake 2**: Complex `sensor.py` with own CONFIG_SCHEMA
- Causes: Multiple validation scopes, conflicts
- Fix: Keep `sensor.py` as stub, sensors in `__init__.py`

❌ **Mistake 3**: `i2c_id`, `address` in `sensor:` block
- Causes: Unrecognized options error
- Fix: Put in `ade7880:` block

## Summary

**ESPHome 2025+ Principle**: 
> *For components with embedded sensors, define everything in one CONFIG_SCHEMA in `__init__.py`. Keep `sensor.py` as a stub or empty.*

This component follows this principle perfectly:
- ✅ Single CONFIG_SCHEMA
- ✅ All options defined once
- ✅ Simple YAML structure
- ✅ No platform conflicts
- ✅ Clean C++ generation

---

**Status**: ✅ Production Ready  
**Architecture**: ✅ Correct for ESPHome 2025+  
**Tested**: ✅ Schema validation passed  
