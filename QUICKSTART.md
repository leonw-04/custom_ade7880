# Quick-Start Integration Guide: ADE7880 Component

## 📦 Schritt 1: Komponente in ESPHome integrieren

### Option A: Local Development (Recommended for Testing)

1. **Komponenten-Verzeichnis erstellen:**
   ```bash
   mkdir -p ~/esphome/custom_components/ade7880
   ```

2. **Dateien kopieren:**
   ```bash
   cp ade7880_calibration.h ~/esphome/custom_components/ade7880/
   cp ade7880_calibration.cpp ~/esphome/custom_components/ade7880/
   cp __init__.py ~/esphome/custom_components/ade7880/
   ```

3. **In ESPHome config referenzieren:**
   ```yaml
   external_components:
     - source:
         type: local
         path: /config/custom_components/ade7880
       components: [ade7880]
   ```

### Option B: Git Repository

```yaml
external_components:
  - source:
      github: leonw-04/custom_ade7880@main
    components: [ade7880]
```

---

## ⚙️ Schritt 2: Minimale YAML-Konfiguration

```yaml
esphome:
  name: esp32-ade7880
  friendly_name: "ADE7880 Meter"
  platform: ESP32
  board: esp32dev

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_encryption_key

ota:
  password: !secret ota_password

logger:
  level: DEBUG
  logs:
    ade7880: DEBUG

# I2C Bus Configuration
i2c:
  id: bus_a
  sda: GPIO21
  scl: GPIO22
  frequency: 100kHz

# External Component
external_components:
  - source:
      type: local
      path: /config/custom_components/ade7880
    components: [ade7880]

# Sensors
sensor:
  - platform: ade7880
    i2c_id: bus_a
    address: 0x38
    update_interval: 60s
    
    voltage_a:
      name: "Voltage A"
    current_a:
      name: "Current A"
    power_a:
      name: "Power A"
```

---

## 🔧 Schritt 3: Hardware-Verkabelung

```
ESP32 Dev Board        ADE7880 Breakout
├─ GPIO 21 (SDA) ----→ SDA
├─ GPIO 22 (SCL) ----→ SCL
├─ GND            ----→ GND
└─ 3.3V (opt.)    ----→ VDD_IO
```

**Pull-up Widerstände:** 4.7 kΩ von SDA/SCL zu 3.3V

---

## ✅ Schritt 4: Deployment & Verifikation

### 4.1 Kompilieren & Flashen

```bash
esphome run config.yaml --device /dev/ttyUSB0
```

### 4.2 Logs prüfen

```
[ade7880] Setting up ADE7880 Energy Meter with Calibration...
[ade7880] Calibration data loaded from Flash
[ade7880] ADE7880 setup complete. Calibration services registered.
[ade7880] Reading sensor values...
[voltage_a] Publishing state 230.123 V
[current_a] Publishing state 10.456 A
[power_a] Publishing state 2406.78 W
```

### 4.3 Services in Home Assistant prüfen

1. Öffne Home Assistant
2. Gehe zu: Developer Tools → Services
3. Suche nach: `ade7880.calibrate_voltage`
4. Sollte 3 Kalibrierungs-Services zeigen:
   - `calibrate_voltage`
   - `calibrate_current`
   - `calibrate_power`
   - `reset_calibration`

---

## 🔬 Schritt 5: Kalibrierung durchführen

### Phase A Spannungs-Kalibrierung

1. **Voltmeter an Phase A anschließen** (230V Leitung)
2. **Referenzwert notieren** → z.B. 230.5 V
3. **Home Assistant Automation erstellen:**

```yaml
automation:
  - alias: "Calibrate Phase A Voltage"
    trigger:
      platform: time
      at: "22:00:00"
    action:
      service: ade7880.calibrate_voltage
      data:
        phase: "A"
        target_voltage: 230.5
```

Oder manuell über Developer Tools → Services:

```yaml
service: ade7880.calibrate_voltage
data:
  phase: "A"
  target_voltage: 230.5
```

### Phase A Strom-Kalibrierung

1. **Stromzange an Phase A Leiter anschließen**
2. **Referenzstrom notieren** → z.B. 10.2 A
3. **Kalibrierungs-Service aufrufen:**

```yaml
service: ade7880.calibrate_current
data:
  phase: "A"
  target_current: 10.2
```

### Phase A Leistungs-Kalibrierung

1. **Bekannte ohmscher Last aktivieren** (z.B. 2000W Heizer)
2. **Leistung mit Referenzmessgerät messen** → z.B. 1987 W
3. **Service aufrufen:**

```yaml
service: ade7880.calibrate_power
data:
  phase: "A"
  target_power: 1987.0
```

### Alle 3 Phasen kalibrieren

```bash
# Phase B
service: ade7880.calibrate_voltage
data:
  phase: "B"
  target_voltage: 230.3

service: ade7880.calibrate_current
data:
  phase: "B"
  target_current: 10.1

service: ade7880.calibrate_power
data:
  phase: "B"
  target_power: 1995.0

# Phase C
service: ade7880.calibrate_voltage
data:
  phase: "C"
  target_voltage: 230.1

service: ade7880.calibrate_current
data:
  phase: "C"
  target_current: 10.3

service: ade7880.calibrate_power
data:
  phase: "C"
  target_power: 2010.0
```

---

## 🎯 Schritt 6: Validierung & Monitoring

### Sensor-Werte überprüfen

Nach der Kalibrierung sollten die Werte **genauer** sein:

**Vorher:**
```
Voltage A: 228.5 V (sollte 230.5 V sein)
Current A: 10.05 A (sollte 10.2 A sein)
Power A: 2300.0 W (sollte 2415.0 W sein)
```

**Nachher:**
```
Voltage A: 230.5 V ✓
Current A: 10.2 A ✓
Power A: 2415.0 W ✓
```

### Home Assistant Dashboard

Erstelle eine Custom Lovelace Card zur Überwachung:

```yaml
type: entities
title: ADE7880 Energy Meter
entities:
  - entity: sensor.voltage_a
    name: Phase A Voltage
  - entity: sensor.current_a
    name: Phase A Current
  - entity: sensor.power_a
    name: Phase A Power
  - entity: sensor.voltage_b
    name: Phase B Voltage
  - entity: sensor.current_b
    name: Phase B Current
  - entity: sensor.power_b
    name: Phase B Power
  - entity: sensor.voltage_c
    name: Phase C Voltage
  - entity: sensor.current_c
    name: Phase C Current
  - entity: sensor.power_c
    name: Phase C Power
```

---

## 🔄 Schritt 7: Automatische Kalibrierung (Optional)

Erstelle eine automatische tägliche Überprüfung:

```yaml
automation:
  - alias: "Daily Calibration Check"
    trigger:
      platform: time
      at: "03:00:00"  # 3 AM
    action:
      - service: ade7880.calibrate_voltage
        data:
          phase: "A"
          target_voltage: 230.5
      - service: ade7880.calibrate_current
        data:
          phase: "A"
          target_current: 10.2
      - delay:
          seconds: 5
      - service: ade7880.calibrate_power
        data:
          phase: "A"
          target_power: 2415.0
      - service: notify.notify
        data:
          message: "Phase A calibration completed"
```

---

## 🛠️ Fehlersuche

### Problem: I2C Fehler beim Starten

```
[i2c] I2C bus (0x0) register read failed
```

**Lösungen:**
1. GPIO-Pins überprüfen (GPIO21/22 sind I2C Standard auf ESP32)
2. Pull-up Widerstände überprüfen (4.7k Ω erforderlich)
3. ADE7880 Stromversorgung überprüfen
4. I2C Frequenz reduzieren:

```yaml
i2c:
  frequency: 50kHz  # Noch konservativer
```

### Problem: Keine Sensoren in Home Assistant

**Lösungen:**
1. External Component geladen? → Logs prüfen
2. Platform korrekt? → `platform: ade7880` (nicht `platform: i2c`)
3. I2C ID referenziert? → `i2c_id: bus_a`
4. ESPHome neu compilieren

### Problem: Kalibrierung wird nicht gespeichert

**Lösungen:**
1. Flash-Speicher voll? → `esphome clean`
2. NVS Partition korrupt? → Device resetten
3. Logs überprüfen:
   ```
   [ade7880] Calibration data saved to Flash
   ```

---

## 📊 Typische Werte für Referenzmessungen

| Messgröße | Typischer Wert | Messgerät |
|-----------|---|---|
| Spannung (L-N) | 230 ± 10 V | Digitales Multimeter |
| Strom | 5-20 A | Stromzange |
| Wirkleistung (ohm.) | V × I × 0.95 | Power Analyzer |
| Blind leistung | 0 W (ohmscher Last) | Power Analyzer |

---

## 🚀 Production Deployment Checkliste

- [ ] Alle 3 Phasen gemessen (VRMS, IRMS, WATT)
- [ ] Kalibrierung durchgeführt und validiert
- [ ] Logs auf Fehler überprüft (keine Warnungen)
- [ ] Sensor-Werte mit Referenzmessgerät verglichen
- [ ] Nach Reboot: Kalibrierung noch aktiv
- [ ] Home Assistant Services funktionieren
- [ ] Update-Intervall angemessen (60s empfohlen)

---

## 📞 Support

**Häufige Fragen:**

**F: Kann ich 2-Draht-Messung verwenden?**
A: Nein, ADE7880 ist für 3-Draht oder 4-Draht ausgelegt.

**F: Wie oft sollte ich neu kalibrieren?**
A: Nach Installation 1× durchführen. Dann bei Bedarf (z.B. halbjährlich) oder nach Lastprofiländerung.

**F: Beeinflussen Kalibrierungen sich gegenseitig?**
A: Nein, jede Phase ist unabhängig. Voltage, Current, Power auch unabhängig.

**F: Kann ich Kalibrierungswerte exportieren?**
A: Ja, die Werte sind in der ESPPreferences NVS-Partition gespeichert. Sie können via API ausgelesen werden (wenn Sie einen Custom Service schreiben).

---

**Viel Erfolg bei der Kalibrierung! 🎉**
