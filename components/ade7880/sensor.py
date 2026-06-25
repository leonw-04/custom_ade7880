"""ESPHome ADE7880 Energy Meter - Sensor Platform.

This file handles:
- Sensor-specific configuration schema
- Creation of sensor entities (voltage, current, power)
- Integration with the main ADE7880Component
"""

from esphome.components import sensor
import esphome.codegen as cg
import esphome.config_validation as cv
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
from . import ADE7880Component, ade7880_ns

# Configuration keys for sensors
CONF_ADE7880_ID = "ade7880_id"
CONF_VOLTAGE_A = "voltage_a"
CONF_VOLTAGE_B = "voltage_b"
CONF_VOLTAGE_C = "voltage_c"
CONF_CURRENT_A = "current_a"
CONF_CURRENT_B = "current_b"
CONF_CURRENT_C = "current_c"
CONF_POWER_A = "power_a"
CONF_POWER_B = "power_b"
CONF_POWER_C = "power_c"

# Optional sensor configuration (all are optional)
SENSOR_SCHEMA = sensor.sensor_schema(
    accuracy_decimals=3,
    state_class=STATE_CLASS_MEASUREMENT,
)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_ADE7880_ID): cv.use_id(ADE7880Component),
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
)


async def to_code(config):
    """Generate C++ code for sensor platform integration.
    
    This function:
    1. Retrieves the ADE7880Component instance
    2. Creates sensor objects for each configured channel
    3. Links sensors to the component's setter methods
    """
    paren = await cg.get_variable(config[CONF_ADE7880_ID])

    # Phase A Voltage Sensor
    if CONF_VOLTAGE_A in config:
        sens = await sensor.new_sensor(config[CONF_VOLTAGE_A])
        cg.add(paren.set_voltage_sensor_a(sens))

    # Phase B Voltage Sensor
    if CONF_VOLTAGE_B in config:
        sens = await sensor.new_sensor(config[CONF_VOLTAGE_B])
        cg.add(paren.set_voltage_sensor_b(sens))

    # Phase C Voltage Sensor
    if CONF_VOLTAGE_C in config:
        sens = await sensor.new_sensor(config[CONF_VOLTAGE_C])
        cg.add(paren.set_voltage_sensor_c(sens))

    # Phase A Current Sensor
    if CONF_CURRENT_A in config:
        sens = await sensor.new_sensor(config[CONF_CURRENT_A])
        cg.add(paren.set_current_sensor_a(sens))

    # Phase B Current Sensor
    if CONF_CURRENT_B in config:
        sens = await sensor.new_sensor(config[CONF_CURRENT_B])
        cg.add(paren.set_current_sensor_b(sens))

    # Phase C Current Sensor
    if CONF_CURRENT_C in config:
        sens = await sensor.new_sensor(config[CONF_CURRENT_C])
        cg.add(paren.set_current_sensor_c(sens))

    # Phase A Power Sensor
    if CONF_POWER_A in config:
        sens = await sensor.new_sensor(config[CONF_POWER_A])
        cg.add(paren.set_power_sensor_a(sens))

    # Phase B Power Sensor
    if CONF_POWER_B in config:
        sens = await sensor.new_sensor(config[CONF_POWER_B])
        cg.add(paren.set_power_sensor_b(sens))

    # Phase C Power Sensor
    if CONF_POWER_C in config:
        sens = await sensor.new_sensor(config[CONF_POWER_C])
        cg.add(paren.set_power_sensor_c(sens))
