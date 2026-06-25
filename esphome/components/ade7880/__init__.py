"""ESPHome ADE7880 Energy Meter - Main Component Configuration.

This file handles:
- Component-level configuration schema
- PollingComponent base registration
- I2C device setup
- Sensor platform definitions (embedded)
"""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import i2c, sensor
from esphome.const import (
    CONF_ID,
    DEVICE_CLASS_VOLTAGE,
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_POWER,
    STATE_CLASS_MEASUREMENT,
    UNIT_VOLT,
    UNIT_AMPERE,
    UNIT_WATT,
)

CODEOWNERS = ["@leonw"]
DEPENDENCIES = ["i2c"]

# Define namespace for C++ code generation
ade7880_ns = cg.esphome_ns.namespace("ade7880")

# Declare the base ADE7880Component class
ADE7880Component = ade7880_ns.class_(
    "ADE7880Component",
    cg.PollingComponent,
    i2c.I2CDevice,
)

# Configuration keys for sensors
CONF_VOLTAGE_A = "voltage_a"
CONF_VOLTAGE_B = "voltage_b"
CONF_VOLTAGE_C = "voltage_c"
CONF_CURRENT_A = "current_a"
CONF_CURRENT_B = "current_b"
CONF_CURRENT_C = "current_c"
CONF_POWER_A = "power_a"
CONF_POWER_B = "power_b"
CONF_POWER_C = "power_c"

# Build sensor schema definitions as a dict to be added to CONFIG_SCHEMA
SENSOR_CONFIG_SCHEMA = {
    cv.Optional(CONF_VOLTAGE_A): sensor.sensor_schema(
        unit_of_measurement=UNIT_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        accuracy_decimals=3,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    cv.Optional(CONF_VOLTAGE_B): sensor.sensor_schema(
        unit_of_measurement=UNIT_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        accuracy_decimals=3,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    cv.Optional(CONF_VOLTAGE_C): sensor.sensor_schema(
        unit_of_measurement=UNIT_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        accuracy_decimals=3,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    cv.Optional(CONF_CURRENT_A): sensor.sensor_schema(
        unit_of_measurement=UNIT_AMPERE,
        device_class=DEVICE_CLASS_CURRENT,
        accuracy_decimals=4,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    cv.Optional(CONF_CURRENT_B): sensor.sensor_schema(
        unit_of_measurement=UNIT_AMPERE,
        device_class=DEVICE_CLASS_CURRENT,
        accuracy_decimals=4,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    cv.Optional(CONF_CURRENT_C): sensor.sensor_schema(
        unit_of_measurement=UNIT_AMPERE,
        device_class=DEVICE_CLASS_CURRENT,
        accuracy_decimals=4,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    cv.Optional(CONF_POWER_A): sensor.sensor_schema(
        unit_of_measurement=UNIT_WATT,
        device_class=DEVICE_CLASS_POWER,
        accuracy_decimals=2,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    cv.Optional(CONF_POWER_B): sensor.sensor_schema(
        unit_of_measurement=UNIT_WATT,
        device_class=DEVICE_CLASS_POWER,
        accuracy_decimals=2,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    cv.Optional(CONF_POWER_C): sensor.sensor_schema(
        unit_of_measurement=UNIT_WATT,
        device_class=DEVICE_CLASS_POWER,
        accuracy_decimals=2,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
}

# Configuration schema for the main component
# Include both component options AND sensor definitions in one schema
CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(ADE7880Component),
        **SENSOR_CONFIG_SCHEMA,  # Unpack all sensor definitions here
    }
).extend(cv.polling_component_schema("60s")).extend(
    i2c.i2c_device_schema(0x38)
)


async def to_code(config):
    """Generate C++ code for the main ADE7880Component.
    
    This function:
    1. Creates an instance of ADE7880Component
    2. Registers it as a PollingComponent
    3. Links it to the I2C bus
    4. Creates and links all sensor instances (if they exist in parent config)
    """
    var = cg.new_Pvariable(config[CONF_ID])
    
    # Register as PollingComponent (cyclic updates)
    await cg.register_component(var, config)
    
    # Link to I2C bus
    await i2c.register_i2c_device(var, config)
    
    # Check parent for sensor configurations (defined in sensor.py)
    # This allows users to define sensors under 'ade7880:' namespace in YAML
    for conf_key, setter_name in [
        (CONF_VOLTAGE_A, "set_voltage_sensor_a"),
        (CONF_VOLTAGE_B, "set_voltage_sensor_b"),
        (CONF_VOLTAGE_C, "set_voltage_sensor_c"),
        (CONF_CURRENT_A, "set_current_sensor_a"),
        (CONF_CURRENT_B, "set_current_sensor_b"),
        (CONF_CURRENT_C, "set_current_sensor_c"),
        (CONF_POWER_A, "set_power_sensor_a"),
        (CONF_POWER_B, "set_power_sensor_b"),
        (CONF_POWER_C, "set_power_sensor_c"),
    ]:
        if conf_key in config:
            sens = await sensor.new_sensor(config[conf_key])
            cg.add(getattr(var, setter_name)(sens))
