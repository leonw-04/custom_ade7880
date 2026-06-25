"""ESPHome ADE7880 Energy Meter - Main Component Configuration.

This file handles:
- Component-level configuration schema
- PollingComponent base registration
- I2C device setup
- Sensor platform definitions
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

# Configuration schema for the main component
# All options must be in ONE Schema dict, not extended separately
CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(ADE7880Component),
        # Phase A Sensors
        cv.Optional(CONF_VOLTAGE_A): sensor.sensor_schema(
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
        cv.Optional(CONF_POWER_A): sensor.sensor_schema(
            unit_of_measurement=UNIT_WATT,
            device_class=DEVICE_CLASS_POWER,
            accuracy_decimals=2,
            state_class=STATE_CLASS_MEASUREMENT,
        ),
        # Phase B Sensors
        cv.Optional(CONF_VOLTAGE_B): sensor.sensor_schema(
            unit_of_measurement=UNIT_VOLT,
            device_class=DEVICE_CLASS_VOLTAGE,
            accuracy_decimals=3,
            state_class=STATE_CLASS_MEASUREMENT,
        ),
        cv.Optional(CONF_CURRENT_B): sensor.sensor_schema(
            unit_of_measurement=UNIT_AMPERE,
            device_class=DEVICE_CLASS_CURRENT,
            accuracy_decimals=4,
            state_class=STATE_CLASS_MEASUREMENT,
        ),
        cv.Optional(CONF_POWER_B): sensor.sensor_schema(
            unit_of_measurement=UNIT_WATT,
            device_class=DEVICE_CLASS_POWER,
            accuracy_decimals=2,
            state_class=STATE_CLASS_MEASUREMENT,
        ),
        # Phase C Sensors
        cv.Optional(CONF_VOLTAGE_C): sensor.sensor_schema(
            unit_of_measurement=UNIT_VOLT,
            device_class=DEVICE_CLASS_VOLTAGE,
            accuracy_decimals=3,
            state_class=STATE_CLASS_MEASUREMENT,
        ),
        cv.Optional(CONF_CURRENT_C): sensor.sensor_schema(
            unit_of_measurement=UNIT_AMPERE,
            device_class=DEVICE_CLASS_CURRENT,
            accuracy_decimals=4,
            state_class=STATE_CLASS_MEASUREMENT,
        ),
        cv.Optional(CONF_POWER_C): sensor.sensor_schema(
            unit_of_measurement=UNIT_WATT,
            device_class=DEVICE_CLASS_POWER,
            accuracy_decimals=2,
            state_class=STATE_CLASS_MEASUREMENT,
        ),
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
    4. Creates and links all sensor instances
    """
    var = cg.new_Pvariable(config[CONF_ID])
    
    # Register as PollingComponent (cyclic updates)
    await cg.register_component(var, config)
    
    # Link to I2C bus
    await i2c.register_i2c_device(var, config)
    
    # Phase A Voltage Sensor
    if CONF_VOLTAGE_A in config:
        sens = await sensor.new_sensor(config[CONF_VOLTAGE_A])
        cg.add(var.set_voltage_sensor_a(sens))
    
    # Phase B Voltage Sensor
    if CONF_VOLTAGE_B in config:
        sens = await sensor.new_sensor(config[CONF_VOLTAGE_B])
        cg.add(var.set_voltage_sensor_b(sens))
    
    # Phase C Voltage Sensor
    if CONF_VOLTAGE_C in config:
        sens = await sensor.new_sensor(config[CONF_VOLTAGE_C])
        cg.add(var.set_voltage_sensor_c(sens))
    
    # Phase A Current Sensor
    if CONF_CURRENT_A in config:
        sens = await sensor.new_sensor(config[CONF_CURRENT_A])
        cg.add(var.set_current_sensor_a(sens))
    
    # Phase B Current Sensor
    if CONF_CURRENT_B in config:
        sens = await sensor.new_sensor(config[CONF_CURRENT_B])
        cg.add(var.set_current_sensor_b(sens))
    
    # Phase C Current Sensor
    if CONF_CURRENT_C in config:
        sens = await sensor.new_sensor(config[CONF_CURRENT_C])
        cg.add(var.set_current_sensor_c(sens))
    
    # Phase A Power Sensor
    if CONF_POWER_A in config:
        sens = await sensor.new_sensor(config[CONF_POWER_A])
        cg.add(var.set_power_sensor_a(sens))
    
    # Phase B Power Sensor
    if CONF_POWER_B in config:
        sens = await sensor.new_sensor(config[CONF_POWER_B])
        cg.add(var.set_power_sensor_b(sens))
    
    # Phase C Power Sensor
    if CONF_POWER_C in config:
        sens = await sensor.new_sensor(config[CONF_POWER_C])
        cg.add(var.set_power_sensor_c(sens))
