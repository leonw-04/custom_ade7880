"""ESPHome ADE7880 Calibration Component Integration."""
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import i2c, sensor, api
from esphome.const import (
    CONF_ID,
    CONF_I2C_ID,
    DEVICE_CLASS_VOLTAGE,
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_POWER,
    STATE_CLASS_MEASUREMENT,
    UNIT_VOLT,
    UNIT_AMPERE,
    UNIT_WATT,
    ICON_POWER,
)

CODEOWNERS = ["@leonw"]
DEPENDENCIES = ["i2c", "api"]

ade7880_ns = cg.esphome_ns.namespace("ade7880")
ADE7880Component = ade7880_ns.class_(
    "ADE7880Component",
    cg.PollingComponent,
    i2c.I2CDevice,
    api.CustomAPIDevice,
)

CONF_VOLTAGE_A = "voltage_a"
CONF_VOLTAGE_B = "voltage_b"
CONF_VOLTAGE_C = "voltage_c"
CONF_CURRENT_A = "current_a"
CONF_CURRENT_B = "current_b"
CONF_CURRENT_C = "current_c"
CONF_POWER_A = "power_a"
CONF_POWER_B = "power_b"
CONF_POWER_C = "power_c"

SENSOR_SCHEMA = sensor.sensor_schema(
    unit_of_measurement=UNIT_VOLT,
    accuracy_decimals=3,
    state_class=STATE_CLASS_MEASUREMENT,
)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(ADE7880Component),
        cv.GenerateID(CONF_I2C_ID): cv.use_id(i2c.I2CBus),
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
).extend(cv.polling_component_schema("60s")).extend(i2c.i2c_device_schema(0x38))


async def to_code(config):
    """Generate C++ code for the ADE7880 component."""
    var = cg.new_Pvt_var(config[CONF_ID])
    await cg.register_component(var, config)
    await i2c.register_i2c_device(var, config)

    # Register sensors
    if CONF_VOLTAGE_A in config:
        sens = await sensor.new_sensor(config[CONF_VOLTAGE_A])
        cg.add(var.set_voltage_sensor_a(sens))

    if CONF_VOLTAGE_B in config:
        sens = await sensor.new_sensor(config[CONF_VOLTAGE_B])
        cg.add(var.set_voltage_sensor_b(sens))

    if CONF_VOLTAGE_C in config:
        sens = await sensor.new_sensor(config[CONF_VOLTAGE_C])
        cg.add(var.set_voltage_sensor_c(sens))

    if CONF_CURRENT_A in config:
        sens = await sensor.new_sensor(config[CONF_CURRENT_A])
        cg.add(var.set_current_sensor_a(sens))

    if CONF_CURRENT_B in config:
        sens = await sensor.new_sensor(config[CONF_CURRENT_B])
        cg.add(var.set_current_sensor_b(sens))

    if CONF_CURRENT_C in config:
        sens = await sensor.new_sensor(config[CONF_CURRENT_C])
        cg.add(var.set_current_sensor_c(sens))

    if CONF_POWER_A in config:
        sens = await sensor.new_sensor(config[CONF_POWER_A])
        cg.add(var.set_power_sensor_a(sens))

    if CONF_POWER_B in config:
        sens = await sensor.new_sensor(config[CONF_POWER_B])
        cg.add(var.set_power_sensor_b(sens))

    if CONF_POWER_C in config:
        sens = await sensor.new_sensor(config[CONF_POWER_C])
        cg.add(var.set_power_sensor_c(sens))
