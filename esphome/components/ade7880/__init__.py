"""ESPHome ADE7880 Energy Meter - Main Component Configuration.

This file handles:
- Component-level configuration schema
- PollingComponent base registration
- I2C device setup
"""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import i2c
from esphome.const import CONF_ID

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

# Configuration schema for the main component
CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(ADE7880Component),
        cv.GenerateID(cv.CONF_I2C_ID): cv.use_id(i2c.I2CBus),
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
    """
    var = cg.new_Pvariable(config[CONF_ID])
    
    # Register as PollingComponent (cyclic updates)
    await cg.register_component(var, config)
    
    # Link to I2C bus
    await i2c.register_i2c_device(var, config)
