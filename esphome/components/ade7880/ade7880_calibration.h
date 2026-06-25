#pragma once

#include "esphome/core/component.h"
#include "esphome/components/i2c/i2c.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/core/preferences.h"
#include <cmath>

namespace esphome {
namespace ade7880 {

// ============================================================================
// Register Addresses (16-bit, Big-Endian transmission)
// ============================================================================

// RMS Value Registers (4 bytes, unsigned)
static constexpr uint16_t REG_AIRMS = 0x43C0;  // Phase A Current RMS
static constexpr uint16_t REG_AVRMS = 0x43C1;  // Phase A Voltage RMS
static constexpr uint16_t REG_BIRMS = 0x43C2;  // Phase B Current RMS
static constexpr uint16_t REG_BVRMS = 0x43C3;  // Phase B Voltage RMS
static constexpr uint16_t REG_CIRMS = 0x43C4;  // Phase C Current RMS
static constexpr uint16_t REG_CVRMS = 0x43C5;  // Phase C Voltage RMS

// Active Power Registers (4 bytes, signed)
static constexpr uint16_t REG_AWATT = 0x43A8;  // Phase A Active Power
static constexpr uint16_t REG_BWATT = 0x43A9;  // Phase B Active Power
static constexpr uint16_t REG_CWATT = 0x43AA;  // Phase C Active Power

// Calibration Gain Registers (4 bytes, internal 24-bit signed)
static constexpr uint16_t REG_AIGAIN = 0x4380; // Phase A Current Gain
static constexpr uint16_t REG_AVGAIN = 0x4381; // Phase A Voltage Gain
static constexpr uint16_t REG_APGAIN = 0x4382; // Phase A Power Gain

static constexpr uint16_t REG_BIGAIN = 0x4383; // Phase B Current Gain
static constexpr uint16_t REG_BVGAIN = 0x4384; // Phase B Voltage Gain
static constexpr uint16_t REG_BPGAIN = 0x4385; // Phase B Power Gain

static constexpr uint16_t REG_CIGAIN = 0x4386; // Phase C Current Gain
static constexpr uint16_t REG_CVGAIN = 0x4387; // Phase C Voltage Gain
static constexpr uint16_t REG_CPGAIN = 0x4388; // Phase C Power Gain

// Configuration Registers
static constexpr uint16_t REG_LCYCMODE = 0xE604; // Line Cycle Mode (1 byte)
static constexpr uint16_t REG_LINECYC = 0xE60C;  // Line Cycle Count (2 bytes)
static constexpr uint16_t REG_COMPMODE = 0xE60E; // Computation Mode (2 bytes)

// ============================================================================
// Calibration Data Structure (persistent storage)
// ============================================================================

struct CalibrationData {
  int32_t aigain = 0;  // Phase A current gain
  int32_t avgain = 0;  // Phase A voltage gain
  int32_t apgain = 0;  // Phase A power gain
  
  int32_t bigain = 0;  // Phase B current gain
  int32_t bvgain = 0;  // Phase B voltage gain
  int32_t bpgain = 0;  // Phase B power gain
  
  int32_t cigain = 0;  // Phase C current gain
  int32_t cvgain = 0;  // Phase C voltage gain
  int32_t cpgain = 0;  // Phase C power gain
};

// ============================================================================
// ADE7880 Calibration Component Class
// ============================================================================

class ADE7880Component : public PollingComponent,
                         public i2c::I2CDevice {
 public:
  ADE7880Component() = default;

  // ========================================================================
  // Component Lifecycle Methods
  // ========================================================================

  void setup() override;
  void update() override;
  void dump_config() override;

  // ========================================================================
  // Sensor Registration (from YAML configuration)
  // ========================================================================

  void set_voltage_sensor_a(sensor::Sensor *sensor) { voltage_sensor_a_ = sensor; }
  void set_voltage_sensor_b(sensor::Sensor *sensor) { voltage_sensor_b_ = sensor; }
  void set_voltage_sensor_c(sensor::Sensor *sensor) { voltage_sensor_c_ = sensor; }

  void set_current_sensor_a(sensor::Sensor *sensor) { current_sensor_a_ = sensor; }
  void set_current_sensor_b(sensor::Sensor *sensor) { current_sensor_b_ = sensor; }
  void set_current_sensor_c(sensor::Sensor *sensor) { current_sensor_c_ = sensor; }

  void set_power_sensor_a(sensor::Sensor *sensor) { power_sensor_a_ = sensor; }
  void set_power_sensor_b(sensor::Sensor *sensor) { power_sensor_b_ = sensor; }
  void set_power_sensor_c(sensor::Sensor *sensor) { power_sensor_c_ = sensor; }

  // ========================================================================
  // Register I/O Methods (Low-level)
  // ========================================================================

  /**
   * Reads from an ADE7880 register via I2C.
   * For 0x43XX and measurement registers (4 bytes):
   *   - Sends 2-byte address (big-endian) + reads 4 bytes response
   * For 0xE6XX and config registers (2 bytes):
   *   - Sends 2-byte address + reads 2 bytes response
   * For other registers (1 byte):
   *   - Sends 2-byte address + reads 1 byte response
   */
  uint32_t read_register(uint16_t reg, uint8_t bytes);

  /**
   * Writes to an ADE7880 register via I2C.
   * Format: [Address_MSB, Address_LSB, Data_MSB, ..., Data_LSB]
   * The 'bytes' parameter specifies how many data bytes to send:
   *   - 4 for 0x43XX (measurement/gain registers)
   *   - 2 for 0xE6XX (config registers)
   *   - 1 for other registers
   */
  bool write_register(uint16_t reg, uint32_t value, uint8_t bytes);

  // ========================================================================
  // Helper: Convert 24-bit signed value from register to int32_t
  // ========================================================================

  static int32_t convert_24bit_signed(uint32_t raw_value);

 private:
  // ========================================================================
  // Persistent Storage
  // ========================================================================

  ESPPreferences preferences_;
  CalibrationData calibration_data_;

  void load_calibration_from_flash_();
  void save_calibration_to_flash_();
  void apply_calibration_to_device_();

  // ========================================================================
  // Sensor Pointers
  // ========================================================================

  sensor::Sensor *voltage_sensor_a_ = nullptr;
  sensor::Sensor *voltage_sensor_b_ = nullptr;
  sensor::Sensor *voltage_sensor_c_ = nullptr;

  sensor::Sensor *current_sensor_a_ = nullptr;
  sensor::Sensor *current_sensor_b_ = nullptr;
  sensor::Sensor *current_sensor_c_ = nullptr;

  sensor::Sensor *power_sensor_a_ = nullptr;
  sensor::Sensor *power_sensor_b_ = nullptr;
  sensor::Sensor *power_sensor_c_ = nullptr;

  // ========================================================================
  // Helper Methods for Calibration
  // ========================================================================

  uint32_t calculate_gain_register(float measured_value, float target_value);
  uint16_t get_phase_index(std::string phase);

  // ========================================================================
  // Register Address Maps
  // ========================================================================

  struct PhaseRegisters {
    uint16_t vrms;
    uint16_t irms;
    uint16_t watt;
    uint16_t vgain;
    uint16_t igain;
    uint16_t pgain;
  };

  PhaseRegisters get_phase_registers(uint16_t phase_idx);
};

// ============================================================================
// Implementation
// ============================================================================

inline uint32_t ADE7880Component::read_register(uint16_t reg, uint8_t bytes) {
  uint8_t addr_buf[2] = {(uint8_t)((reg >> 8) & 0xFF), (uint8_t)(reg & 0xFF)};
  uint8_t data_buf[4] = {0};

  // Write register address
  if (!this->write(addr_buf, 2)) {
    ESP_LOGE("ade7880", "Failed to write register address 0x%04X", reg);
    return 0;
  }

  // Read data
  if (!this->read(data_buf, bytes)) {
    ESP_LOGE("ade7880", "Failed to read register 0x%04X", reg);
    return 0;
  }

  // Convert bytes to uint32_t (big-endian)
  uint32_t value = 0;
  for (uint8_t i = 0; i < bytes; i++) {
    value = (value << 8) | data_buf[i];
  }

  return value;
}

inline bool ADE7880Component::write_register(uint16_t reg, uint32_t value,
                                               uint8_t bytes) {
  uint8_t buffer[6];

  // Construct I2C write buffer: [Addr_MSB, Addr_LSB, Data...]
  buffer[0] = (uint8_t)((reg >> 8) & 0xFF);     // Register address MSB
  buffer[1] = (uint8_t)(reg & 0xFF);             // Register address LSB

  // Add data bytes in big-endian order
  if (bytes == 4) {
    buffer[2] = (uint8_t)((value >> 24) & 0xFF);
    buffer[3] = (uint8_t)((value >> 16) & 0xFF);
    buffer[4] = (uint8_t)((value >> 8) & 0xFF);
    buffer[5] = (uint8_t)(value & 0xFF);
  } else if (bytes == 2) {
    buffer[2] = (uint8_t)((value >> 8) & 0xFF);
    buffer[3] = (uint8_t)(value & 0xFF);
  } else if (bytes == 1) {
    buffer[2] = (uint8_t)(value & 0xFF);
  }

  return this->write(buffer, 2 + bytes);
}

inline int32_t ADE7880Component::convert_24bit_signed(uint32_t raw_value) {
  // Extract lower 24 bits
  int32_t value = raw_value & 0xFFFFFF;

  // Check if the sign bit (bit 23) is set
  if (value & 0x800000) {
    // Sign-extend: set upper 8 bits to 1s for negative numbers
    value |= 0xFF000000;
  }

  return value;
}

inline uint32_t ADE7880Component::calculate_gain_register(float measured_value,
                                                           float target_value) {
  if (measured_value == 0.0f) {
    ESP_LOGW("ade7880", "Measured value is zero, cannot calibrate");
    return 0;
  }

  // Formula: Gain_Register = ((target / measured) - 1) * 2^23
  float ratio = target_value / measured_value;
  int32_t gain = (int32_t)((ratio - 1.0f) * 8388608.0f); // 2^23 = 8388608

  // Limit gain to 24-bit signed range [-0x800000, 0x7FFFFF]
  if (gain > 0x7FFFFF) gain = 0x7FFFFF;
  if (gain < -0x800000) gain = -0x800000;

  return (uint32_t)gain;
}

inline uint16_t ADE7880Component::get_phase_index(std::string phase) {
  if (phase == "A" || phase == "a") return 0;
  if (phase == "B" || phase == "b") return 1;
  if (phase == "C" || phase == "c") return 2;
  return 0xFF; // Invalid
}

inline ADE7880Component::PhaseRegisters ADE7880Component::get_phase_registers(
    uint16_t phase_idx) {
  if (phase_idx == 0) {
    return {REG_AVRMS, REG_AIRMS, REG_AWATT, REG_AVGAIN, REG_AIGAIN, REG_APGAIN};
  } else if (phase_idx == 1) {
    return {REG_BVRMS, REG_BIRMS, REG_BWATT, REG_BVGAIN, REG_BIGAIN, REG_BPGAIN};
  } else {
    return {REG_CVRMS, REG_CIRMS, REG_CWATT, REG_CVGAIN, REG_CIGAIN, REG_CPGAIN};
  }
}

}  // namespace ade7880
}  // namespace esphome
