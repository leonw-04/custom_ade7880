# ADE7880 External Component - Integration Tutorial (2025+)

Dieses Tutorial zeigt die Installation und Nutzung der neuen External Component Architektur.

## 🗂️ Projektstruktur Setup

### Schritt 1: Verzeichnisse erstellen

```bash
# ESPHome Projekt Verzeichnis
mkdir -p my_esphome_project
cd my_esphome_project

# Custom Components Ordner
mkdir -p custom_components/ade7880
```

### Schritt 2: Component Dateien kopieren

```bash
# Von custom_ade7880 Repository
cp -r custom_ade7880/components/ade7880 my_esphome_project/custom_components/
```

### Finale Projektstruktur

```
my_esphome_project/
├── config.yaml                          ← ESPHome Konfiguration
└── custom_components/
    └── ade7880/
        ├── __init__.py                  ← Component-Init
        ├── sensor.py                    ← Sensor Platform
        ├── ade7880_calibration.h        ← C++ Header
        └── ade7880_calibration.cpp      ← C++ Implementation
```

## 📝 YAML Konfiguration

### `config.yaml` Minimal

```yaml
esphome:
  name: energy-meter
  platform: ESP32
  board: esp32dev

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_encryption_key

logger:
  level: DEBUG
  logs:
    ade7880: DEBUG

# I2C Bus (GPIO21=SDA, GPIO22=SCL)
i2c:
  sda: GPIO21
  scl: GPIO22
  frequency: 100kHz

# External Component registrieren
external_components:
  - source:
      type: local
      path: ./custom_components/ade7880
    components: [ade7880]

# Sensoren konfigurieren
sensor:
  - platform: ade7880
    update_interval: 60s
    
    # Phase A (alle 3 Kanäle optional)
    voltage_a:
      name: "Voltage Phase A"
    current_a:
      name: "Current Phase A"
    power_a:
      name: "Power Phase A"
    
    # Phase B (optional)
    voltage_b:
      name: "Voltage Phase B"
    current_b:
      name: "Current Phase B"
    power_b:
      name: "Power Phase B"
    
    # Phase C (optional)
    voltage_c:
      name: "Voltage Phase C"
    current_c:
      name: "Current Phase C"
    power_c:
      name: "Power Phase C"
```

## 🔌 Hardware Verkabelung

```
ESP32 Dev Board              ADE7880 Breakout
┌─────────────┐             ┌──────────────┐
│             │             │              │
│  GPIO 21    ├─────────────┤ SDA          │
│  (SDA)      │    4.7kΩ    │              │
│             │   Pull-Up   │              │
│             │             │              │
│  GPIO 22    ├─────────────┤ SCL          │
│  (SCL)      │    4.7kΩ    │              │
│             │   Pull-Up   │              │
│             │             │              │
│  GND        ├─────────────┤ GND          │
│             │             │              │
│  3.3V       ├─────────────┤ VDD_IO       │
│             │  (optional) │              │
└─────────────┘             └──────────────┘
```

**Wichtig:** 4.7kΩ Pull-up Widerstände von SDA/SCL zu 3.3V erforderlich!

## 🚀 Deployment

### Schritt 1: Kompilieren

```bash
cd my_esphome_project
esphome compile config.yaml
```

**Erwartete Ausgabe:**
```
INFO Compiling .esphome/build/energy-meter/.pioenvs/energy-meter/firmware.elf
...
INFO Successfully compiled program.
```

### Schritt 2: Flashen auf ESP32

```bash
esphome upload config.yaml --device /dev/ttyUSB0
```

Oder direkt kompilieren + flashen:

```bash
esphome run config.yaml --device /dev/ttyUSB0
```

## 📊 Logs Monitoring

```bash
esphome logs config.yaml --device /dev/ttyUSB0
```

**Erwartete Startup-Sequenz:**

```
[ade7880] Setting up ADE7880 Energy Meter with Calibration...
[ade7880] Calibration data loaded from Flash
[ade7880] ADE7880 setup complete. Calibration services registered.
[i2c] I2C scan complete
[sensor] Voltage A: publishing state 230.123 V
[sensor] Current A: publishing state 10.456 A
[sensor] Power A: publishing state 2406.78 W
```

## 🔧 Kalibrierungs-Services testen

### In Home Assistant

1. Gehe zu: **Entwickler-Tools** → **Services**
2. Suche nach: `ade7880.calibrate_voltage`
3. Wähle **ADE7880 Energy Meter** Gerät
4. Gib Parameter ein:

```yaml
service: ade7880.calibrate_voltage
data:
  phase: "A"
  target_voltage: 230.5
```

### Über Automation

```yaml
automation:
  - alias: "Morning Calibration Check"
    trigger:
      platform: time
      at: "06:00:00"
    action:
      - service: ade7880.calibrate_voltage
        data:
          phase: "A"
          target_voltage: 230.5
      - service: ade7880.calibrate_current
        data:
          phase: "A"
          target_current: 10.5
      - service: ade7880.calibrate_power
        data:
          phase: "A"
          target_power: 2415.0
      - service: notify.notify
        data:
          message: "Phase A calibration completed"
```

## ✅ Verifikations-Schritte

### 1. I2C Kommunikation prüfen

Logs sollten zeigen:
```
[i2c] I2C device at address 0x38 ready
```

### 2. Sensoren aktiv?

Home Assistant zeigt Sensoren:
```
sensor.energy_meter_voltage_phase_a
sensor.energy_meter_current_phase_a
sensor.energy_meter_power_phase_a
```

### 3. Werte sinnvoll?

Typische Messwerte:
- **Voltage:** 220-240 V
- **Current:** 1-20 A
- **Power:** 100-5000 W

### 4. Kalibrierungs-Service verfügbar?

Home Assistant Developer Tools sollte Services zeigen:
```
ade7880.calibrate_voltage
ade7880.calibrate_current
ade7880.calibrate_power
ade7880.reset_calibration
```

### 5. Nach Reboot persistiert?

Neustart und prüfen:
```
[ade7880] Calibration data loaded from Flash
```

## 🐛 Fehlersuche

### Problem: "Could not load external component"

**Ursache:** Komponenten-Pfad falsch
**Lösung:**
```yaml
external_components:
  - source:
      type: local
      path: ./custom_components/ade7880  # ← Punkt-Pfad!
    components: [ade7880]
```

### Problem: "I2C device not found"

**Ursache:** I2C Adresse falsch oder Gerät nicht verbunden
**Lösung:**
1. I2C Scan aktivieren:
```yaml
i2c:
  scan: true  # ← Findet alle Geräte
```
2. Logs überprüfen:
```
[i2c] Found i2c device at address 0x38
```

### Problem: "No module named 'ade7880'"

**Ursache:** `__init__.py` nicht vorhanden
**Lösung:**
```bash
ls custom_components/ade7880/
# Sollte zeigen: __init__.py sensor.py ade7880_calibration.h ...
```

### Problem: Sensoren zeigen 0

**Ursache:** Register nicht richtig ausgelesen
**Lösung:**
1. Debug-Logs aktivieren:
```yaml
logger:
  level: DEBUG
  logs:
    ade7880: DEBUG
    i2c: DEBUG
```
2. Register-Wert prüfen (im Code)

## 📈 Dashboard Erstellen

Home Assistant Lovelace Card:

```yaml
type: entities
title: ADE7880 Energy Meter
entities:
  - entity: sensor.voltage_phase_a
  - entity: sensor.current_phase_a
  - entity: sensor.power_phase_a
  - entity: sensor.voltage_phase_b
  - entity: sensor.current_phase_b
  - entity: sensor.power_phase_b
  - entity: sensor.voltage_phase_c
  - entity: sensor.current_phase_c
  - entity: sensor.power_phase_c
```

Oder mit Kalibrierungs-Buttons:

```yaml
type: vertical-stack
cards:
  - type: entities
    title: Measurements
    entities:
      - sensor.voltage_phase_a
      - sensor.current_phase_a
      - sensor.power_phase_a

  - type: custom:button-card
    entity: sensor.voltage_phase_a
    name: Calibrate Voltage A
    tap_action:
      action: call-service
      service: ade7880.calibrate_voltage
      service_data:
        phase: "A"
        target_voltage: 230.5
```

## 🔄 Git Repository Nutzung

Statt lokal, direkt aus Git:

```yaml
external_components:
  - source:
      github: leonw-04/custom_ade7880@main
      path: components/ade7880
    components: [ade7880]
```

Repository muss folgende Struktur haben:

```
custom_ade7880/
└── components/
    └── ade7880/
        ├── __init__.py
        ├── sensor.py
        ├── ade7880_calibration.h
        └── ade7880_calibration.cpp
```

## 📚 Weiterführende Ressourcen

- **EXTERNAL_COMPONENT_GUIDE.md** - Architecture Erklärung
- **IMPLEMENTATION_NOTES.md** - Technische Details
- **example_config.yaml** - Komplettes Arbeitsbeispiel
- ESPHome Docs: https://esphome.io/components/external_components.html

## 🎯 Production Checkliste

- [ ] Komponenten-Ordner erstellt
- [ ] Alle 4 Dateien kopiert (`__init__.py`, `sensor.py`, `.h`, `.cpp`)
- [ ] `config.yaml` mit I2C und Sensoren
- [ ] `external_components` registriert
- [ ] Build erfolgreich (keine Fehler)
- [ ] Auf ESP32 geflasht
- [ ] Logs zeigen "ADE7880 setup complete"
- [ ] Sensoren in HA sichtbar mit sinnvollen Werten
- [ ] Kalibrierungs-Services verfügbar
- [ ] Nach Reboot: Kalibrierung erhalten
- [ ] Dashboard eingerichtet

---

**Status:** ✅ Ready für Production
**Version:** 1.0 (2025+ Architecture)
**Lizenz:** MIT
