#include "ade7880_calibration.h"
#include "esphome/core/log.h"

namespace esphome {
namespace ade7880 {

static const char *const TAG = "ade7880";

// ============================================================================
// Component Lifecycle Methods
// ============================================================================

void ADE7880Component::setup() {
  ESP_LOGI(TAG, "Setting up ADE7880 Energy Meter with Calibration...");

  // Load calibration data from Flash
  load_calibration_from_flash_();

  // Apply calibration to the device immediately after setup
  apply_calibration_to_device_();

  // Register Home Assistant CustomAPI services for calibration
  register_service<std::string, float>(
      &ADE7880Component::calibrate_voltage, "calibrate_voltage",
      {"phase", "target_voltage"});
  register_service<std::string, float>(
      &ADE7880Component::calibrate_current, "calibrate_current",
      {"phase", "target_current"});
  register_service<std::string, float>(
      &ADE7880Component::calibrate_power, "calibrate_power",
      {"phase", "target_power"});
  register_service(&ADE7880Component::reset_calibration, "reset_calibration");

  ESP_LOGI(TAG, "ADE7880 setup complete. Calibration services registered.");
}

void ADE7880Component::update() {
  // Read and update voltage sensors (VRMS registers return values in 0.001V units)
  if (voltage_sensor_a_ != nullptr) {
    uint32_t raw = read_register(REG_AVRMS, 4);
    float voltage = (float)raw * 0.001f;  // Convert to Volts
    voltage_sensor_a_->publish_state(voltage);
  }

  if (voltage_sensor_b_ != nullptr) {
    uint32_t raw = read_register(REG_BVRMS, 4);
    float voltage = (float)raw * 0.001f;
    voltage_sensor_b_->publish_state(voltage);
  }

  if (voltage_sensor_c_ != nullptr) {
    uint32_t raw = read_register(REG_CVRMS, 4);
    float voltage = (float)raw * 0.001f;
    voltage_sensor_c_->publish_state(voltage);
  }

  // Read and update current sensors (IRMS registers return values in 0.0001A units)
  if (current_sensor_a_ != nullptr) {
    uint32_t raw = read_register(REG_AIRMS, 4);
    float current = (float)raw * 0.0001f;  // Convert to Amperes
    current_sensor_a_->publish_state(current);
  }

  if (current_sensor_b_ != nullptr) {
    uint32_t raw = read_register(REG_BIRMS, 4);
    float current = (float)raw * 0.0001f;
    current_sensor_b_->publish_state(current);
  }

  if (current_sensor_c_ != nullptr) {
    uint32_t raw = read_register(REG_CIRMS, 4);
    float current = (float)raw * 0.0001f;
    current_sensor_c_->publish_state(current);
  }

  // Read and update power sensors (WATT registers return values in 0.01W units)
  if (power_sensor_a_ != nullptr) {
    uint32_t raw = read_register(REG_AWATT, 4);
    int32_t signed_value = convert_24bit_signed(raw);
    float power = (float)signed_value * 0.01f;  // Convert to Watts
    power_sensor_a_->publish_state(power);
  }

  if (power_sensor_b_ != nullptr) {
    uint32_t raw = read_register(REG_BWATT, 4);
    int32_t signed_value = convert_24bit_signed(raw);
    float power = (float)signed_value * 0.01f;
    power_sensor_b_->publish_state(power);
  }

  if (power_sensor_c_ != nullptr) {
    uint32_t raw = read_register(REG_CWATT, 4);
    int32_t signed_value = convert_24bit_signed(raw);
    float power = (float)signed_value * 0.01f;
    power_sensor_c_->publish_state(power);
  }
}

void ADE7880Component::dump_config() {
  ESP_LOGCONFIG(TAG, "ADE7880 Energy Meter (I2C)");
  LOG_I2C_DEVICE(this);
  LOG_UPDATE_INTERVAL(this);

  ESP_LOGCONFIG(TAG, "Current Calibration Values:");
  ESP_LOGCONFIG(TAG, "  Phase A: VGAIN=0x%06X IGAIN=0x%06X PGAIN=0x%06X",
                (calibration_data_.avgain & 0xFFFFFF),
                (calibration_data_.aigain & 0xFFFFFF),
                (calibration_data_.apgain & 0xFFFFFF));
  ESP_LOGCONFIG(TAG, "  Phase B: VGAIN=0x%06X IGAIN=0x%06X PGAIN=0x%06X",
                (calibration_data_.bvgain & 0xFFFFFF),
                (calibration_data_.bigain & 0xFFFFFF),
                (calibration_data_.bpgain & 0xFFFFFF));
  ESP_LOGCONFIG(TAG, "  Phase C: VGAIN=0x%06X IGAIN=0x%06X PGAIN=0x%06X",
                (calibration_data_.cvgain & 0xFFFFFF),
                (calibration_data_.cigain & 0xFFFFFF),
                (calibration_data_.cpgain & 0xFFFFFF));
}

// ============================================================================
// Persistent Storage Methods
// ============================================================================

void ADE7880Component::load_calibration_from_flash_() {
  auto calib_pref = global_preferences->make_preference<CalibrationData>(
      0x44415E37, crc8("ade7880_calib"));  // CRC hash of "ade7880_calib"

  if (calib_pref.load(&calibration_data_)) {
    ESP_LOGI(TAG, "Calibration data loaded from Flash");
    ESP_LOGD(TAG,
             "Loaded A: VGAIN=0x%06X IGAIN=0x%06X PGAIN=0x%06X",
             (calibration_data_.avgain & 0xFFFFFF),
             (calibration_data_.aigain & 0xFFFFFF),
             (calibration_data_.apgain & 0xFFFFFF));
  } else {
    ESP_LOGI(TAG, "No calibration data in Flash, using defaults (0)");
    calibration_data_ = CalibrationData();
  }
}

void ADE7880Component::save_calibration_to_flash_() {
  auto calib_pref = global_preferences->make_preference<CalibrationData>(
      0x44415E37, crc8("ade7880_calib"));

  if (calib_pref.save(&calibration_data_)) {
    ESP_LOGI(TAG, "Calibration data saved to Flash");
  } else {
    ESP_LOGE(TAG, "Failed to save calibration data to Flash");
  }
}

void ADE7880Component::apply_calibration_to_device_() {
  ESP_LOGI(TAG, "Applying calibration values to ADE7880...");

  // Apply Phase A gains
  write_register(REG_AVGAIN, (uint32_t)calibration_data_.avgain, 4);
  write_register(REG_AIGAIN, (uint32_t)calibration_data_.aigain, 4);
  write_register(REG_APGAIN, (uint32_t)calibration_data_.apgain, 4);

  // Apply Phase B gains
  write_register(REG_BVGAIN, (uint32_t)calibration_data_.bvgain, 4);
  write_register(REG_BIGAIN, (uint32_t)calibration_data_.bigain, 4);
  write_register(REG_BPGAIN, (uint32_t)calibration_data_.bpgain, 4);

  // Apply Phase C gains
  write_register(REG_CVGAIN, (uint32_t)calibration_data_.cvgain, 4);
  write_register(REG_CIGAIN, (uint32_t)calibration_data_.cigain, 4);
  write_register(REG_CPGAIN, (uint32_t)calibration_data_.cpgain, 4);

  ESP_LOGI(TAG, "Calibration applied to device");
}

// ============================================================================
// Calibration Service Methods
// ============================================================================

void ADE7880Component::calibrate_voltage(std::string phase,
                                         float target_voltage) {
  ESP_LOGI(TAG, "Starting voltage calibration for phase %s (target: %.2f V)",
           phase.c_str(), target_voltage);

  uint16_t phase_idx = get_phase_index(phase);
  if (phase_idx == 0xFF) {
    ESP_LOGE(TAG, "Invalid phase: %s", phase.c_str());
    return;
  }

  PhaseRegisters regs = get_phase_registers(phase_idx);

  // Read current (uncalibrated) voltage
  uint32_t raw_voltage = read_register(regs.vrms, 4);
  float measured_voltage = (float)raw_voltage * 0.001f;

  ESP_LOGD(TAG, "Measured voltage for phase %s: %.3f V", phase.c_str(),
           measured_voltage);

  if (measured_voltage < 0.01f) {
    ESP_LOGE(TAG, "Measured voltage too low or zero, calibration aborted");
    return;
  }

  // Calculate new gain
  uint32_t new_gain = calculate_gain_register(measured_voltage, target_voltage);

  ESP_LOGI(TAG, "Calculated VGAIN for phase %s: 0x%06X", phase.c_str(),
           (new_gain & 0xFFFFFF));

  // Apply to device
  write_register(regs.vgain, new_gain, 4);

  // Update in-memory calibration data
  if (phase_idx == 0) {
    calibration_data_.avgain = (int32_t)new_gain;
  } else if (phase_idx == 1) {
    calibration_data_.bvgain = (int32_t)new_gain;
  } else {
    calibration_data_.cvgain = (int32_t)new_gain;
  }

  // Save to Flash
  save_calibration_to_flash_();

  ESP_LOGI(TAG, "Voltage calibration for phase %s complete", phase.c_str());
}

void ADE7880Component::calibrate_current(std::string phase,
                                         float target_current) {
  ESP_LOGI(TAG, "Starting current calibration for phase %s (target: %.4f A)",
           phase.c_str(), target_current);

  uint16_t phase_idx = get_phase_index(phase);
  if (phase_idx == 0xFF) {
    ESP_LOGE(TAG, "Invalid phase: %s", phase.c_str());
    return;
  }

  PhaseRegisters regs = get_phase_registers(phase_idx);

  // Read current (uncalibrated) current measurement
  uint32_t raw_current = read_register(regs.irms, 4);
  float measured_current = (float)raw_current * 0.0001f;

  ESP_LOGD(TAG, "Measured current for phase %s: %.4f A", phase.c_str(),
           measured_current);

  if (measured_current < 0.001f) {
    ESP_LOGE(TAG, "Measured current too low or zero, calibration aborted");
    return;
  }

  // Calculate new gain
  uint32_t new_gain = calculate_gain_register(measured_current, target_current);

  ESP_LOGI(TAG, "Calculated IGAIN for phase %s: 0x%06X", phase.c_str(),
           (new_gain & 0xFFFFFF));

  // Apply to device
  write_register(regs.igain, new_gain, 4);

  // Update in-memory calibration data
  if (phase_idx == 0) {
    calibration_data_.aigain = (int32_t)new_gain;
  } else if (phase_idx == 1) {
    calibration_data_.bigain = (int32_t)new_gain;
  } else {
    calibration_data_.cigain = (int32_t)new_gain;
  }

  // Save to Flash
  save_calibration_to_flash_();

  ESP_LOGI(TAG, "Current calibration for phase %s complete", phase.c_str());
}

void ADE7880Component::calibrate_power(std::string phase,
                                       float target_power) {
  ESP_LOGI(TAG, "Starting power calibration for phase %s (target: %.2f W)",
           phase.c_str(), target_power);

  uint16_t phase_idx = get_phase_index(phase);
  if (phase_idx == 0xFF) {
    ESP_LOGE(TAG, "Invalid phase: %s", phase.c_str());
    return;
  }

  PhaseRegisters regs = get_phase_registers(phase_idx);

  // Read current (uncalibrated) power measurement
  uint32_t raw_power = read_register(regs.watt, 4);
  int32_t signed_power = convert_24bit_signed(raw_power);
  float measured_power = (float)signed_power * 0.01f;

  ESP_LOGD(TAG, "Measured power for phase %s: %.2f W", phase.c_str(),
           measured_power);

  if (std::abs(measured_power) < 0.1f) {
    ESP_LOGE(TAG, "Measured power too low or zero, calibration aborted");
    return;
  }

  // Calculate new gain
  uint32_t new_gain = calculate_gain_register(measured_power, target_power);

  ESP_LOGI(TAG, "Calculated PGAIN for phase %s: 0x%06X", phase.c_str(),
           (new_gain & 0xFFFFFF));

  // Apply to device
  write_register(regs.pgain, new_gain, 4);

  // Update in-memory calibration data
  if (phase_idx == 0) {
    calibration_data_.apgain = (int32_t)new_gain;
  } else if (phase_idx == 1) {
    calibration_data_.bpgain = (int32_t)new_gain;
  } else {
    calibration_data_.cpgain = (int32_t)new_gain;
  }

  // Save to Flash
  save_calibration_to_flash_();

  ESP_LOGI(TAG, "Power calibration for phase %s complete", phase.c_str());
}

void ADE7880Component::reset_calibration() {
  ESP_LOGI(TAG, "Resetting all calibration values...");

  // Reset all gains to zero in device
  write_register(REG_AVGAIN, 0, 4);
  write_register(REG_AIGAIN, 0, 4);
  write_register(REG_APGAIN, 0, 4);

  write_register(REG_BVGAIN, 0, 4);
  write_register(REG_BIGAIN, 0, 4);
  write_register(REG_BPGAIN, 0, 4);

  write_register(REG_CVGAIN, 0, 4);
  write_register(REG_CIGAIN, 0, 4);
  write_register(REG_CPGAIN, 0, 4);

  // Reset in-memory data
  calibration_data_ = CalibrationData();

  // Save to Flash
  save_calibration_to_flash_();

  ESP_LOGI(TAG, "Calibration reset complete");
}

}  // namespace ade7880
}  // namespace esphome
