# ADE7880 ESPHome External Component (2025+)

Eine **produktionsreife Custom Component** für ESPHome (neue Architektur seit 2025) zur Steuerung des **Analog Devices ADE7880** 3-Phasen-Energiemess-ICs mit On-Board-Kalibrierung.

## 📦 Neue External Component Architektur

Diese Component folgt der seit 2025 aktualisierten ESPHome External Component Struktur:

```
custom_components/ade7880/
├── __init__.py              ← Main component config schema
├── sensor.py                ← Sensor platform integration
├── ade7880_calibration.h    ← C++ Header
└── ade7880_calibration.cpp  ← C++ Implementation
```

### Unterschied zur alten Struktur

| Aspekt | Alt (pre-2025) | Neu (2025+) |
|--------|---|---|
| **Python Integration** | Ein großes `__init__.py` | Separate `__init__.py`, `sensor.py` |
| **Plattformen** | Manuell konfiguriert | Automatisch via `sensor.py` geladen |
| **Codegen** | `new_Pvt_var()` | `new_Pvariable()` |
| **Sensor-Link** | `set_*()` Setter Calls | `cg.add(parent.set_*())` Pattern |

## 🚀 Installation

### 1. Komponente im ESPHome Projekt kopieren

```bash
mkdir -p my_esphome_project/custom_components/ade7880
cp -r custom_components/ade7880/* my_esphome_project/custom_components/ade7880/
```

### 2. External Component registrieren (YAML)

```yaml
external_components:
  - source:
      type: local
      path: ./custom_components/ade7880
    components: [ade7880]
```

Oder direkt aus Git:

```yaml
external_components:
  - source:
      github: leonw-04/custom_ade7880@main
      path: components/ade7880
    components: [ade7880]
```

## 📋 Minimale YAML Konfiguration

```yaml
i2c:
  sda: GPIO21
  scl: GPIO22
  frequency: 100kHz

sensor:
  - platform: ade7880
    address: 0x38
    update_interval: 60s
    
    voltage_a:
      name: "Phase A Voltage"
    current_a:
      name: "Phase A Current"
    power_a:
      name: "Phase A Power"
```

## 🔧 Python Integration Erklärung

### `__init__.py` – Haupt-Component

```python
# 1. Namespace definieren
ade7880_ns = cg.esphome_ns.namespace("ade7880")

# 2. Klassendefinition
ADE7880Component = ade7880_ns.class_(
    "ADE7880Component",
    cg.PollingComponent,
    i2c.I2CDevice,
)

# 3. Config Schema
CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(ADE7880Component),
    cv.GenerateID(cv.CONF_I2C_ID): cv.use_id(i2c.I2CBus),
}).extend(cv.polling_component_schema("60s")).extend(
    i2c.i2c_device_schema(0x38)
)

# 4. Code Generation
async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await i2c.register_i2c_device(var, config)
```

**Was hier passiert:**
- Erstellt `ADE7880Component` Klasse im C++
- Registriert sie als `PollingComponent` (zyklische Updates)
- Verbindet sie mit I2C Bus

### `sensor.py` – Sensor Plattform

```python
# 1. Sensor-spezifische Config
CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.use_id(ADE7880Component),  # ← Link zum Component!
    cv.Optional(CONF_VOLTAGE_A): sensor.sensor_schema(...),
    # ...
})

# 2. Sensor erstellen und verlinken
async def to_code(config):
    paren = await cg.get_variable(config[CONF_ID])  # ← Get Component instance
    
    if CONF_VOLTAGE_A in config:
        sens = await sensor.new_sensor(config[CONF_VOLTAGE_A])
        cg.add(paren.set_voltage_sensor_a(sens))  # ← Link sensor to component
```

**Was hier passiert:**
- Erhält Referenz zur `ADE7880Component` Instanz
- Erstellt Sensor-Objekte
- Verlinkt Sensoren via `set_*()` Methoden

## 💡 Warum diese Aufteilung?

| Datei | Verantwortung |
|-------|---|
| **`__init__.py`** | Komponenten-Initialisierung und allgemeine Config |
| **`sensor.py`** | Sensor-Plattform: welche Sensoren sind verfügbar? |
| **`ade7880_calibration.h`** | C++ Header: Register, Datenstrukturen |
| **`ade7880_calibration.cpp`** | C++ Implementation: Logic, I2C, Calibration |

## 📊 Register Mapping (wie zuvor)

### Messwert-Register (Read-Only)

| Register | Adresse | Einheit | Skalierung |
|----------|---------|--------|-----------|
| AVRMS | 0x43C1 | V | × 0.001 |
| AIRMS | 0x43C0 | A | × 0.0001 |
| AWATT | 0x43A8 | W | × 0.01 |
| (B und C ebenso) | ... | ... | ... |

### Gain-Register (Read/Write)

| Register | Adresse | Zweck |
|----------|---------|-------|
| AVGAIN | 0x4381 | Spannung Phase A |
| AIGAIN | 0x4380 | Strom Phase A |
| APGAIN | 0x4382 | Leistung Phase A |
| (B und C ebenso) | ... | ... |

## 🔬 Kalibrierungs-Services

Home Assistant Services (wie zuvor, keine Änderung):

```yaml
# Spannungs-Kalibrierung
service: ade7880.calibrate_voltage
data:
  phase: "A"
  target_voltage: 230.5

# Strom-Kalibrierung
service: ade7880.calibrate_current
data:
  phase: "A"
  target_current: 10.5

# Leistungs-Kalibrierung
service: ade7880.calibrate_power
data:
  phase: "A"
  target_power: 2415.0

# Reset
service: ade7880.reset_calibration
```

## 📈 Persistente Speicherung

Kalibrierungswerte werden in Flash gespeichert (ESPPreferences):

```cpp
auto pref = global_preferences->make_preference<CalibrationData>(
    0x44415E37, crc8("ade7880_calib"));
pref.save(&calibration_data_);  // Schreiben
pref.load(&calibration_data_);  // Lesen (beim Boot)
```

**Automatisches Laden:**
In `setup()` werden gespeicherte Gains sofort in alle 9 Register geschrieben.

## ✅ Validierungs-Checkliste

- [x] Externe Component Struktur korrekt
- [x] `__init__.py` mit `CONFIG_SCHEMA` und `to_code()`
- [x] `sensor.py` mit Sensor-Config
- [x] C++ Header mit richtiger Namespace
- [x] C++ Implementation mit allen Methoden
- [x] I2C Register I/O (Big-Endian)
- [x] 24-Bit Sign-Extension
- [x] Kalibrierungs-Mathematik
- [x] ESPPreferences Persistenz
- [x] Home Assistant Services

## 🛠️ Debugging

### ESPHome Logs anschauen

```bash
esphome logs config.yaml --device /dev/ttyUSB0
```

Erwartete Ausgabe:

```
[ade7880] Setting up ADE7880 Energy Meter...
[ade7880] Calibration data loaded from Flash
[ade7880] ADE7880 setup complete
[voltage_a] Publishing state 230.123 V
[current_a] Publishing state 10.456 A
[power_a] Publishing state 2406.78 W
```

### I2C Scan

```yaml
logger:
  logs:
    i2c: DEBUG
```

## 📚 Weitere Dokumentation

- **QUICKSTART.md** – Schritt-für-Schritt Installation
- **IMPLEMENTATION_NOTES.md** – Technische Details
- **PROJECT_SUMMARY.md** – Feature-Übersicht
- **VALIDATION.md** – Validierungs-Checkliste

## 🎯 Nächste Schritte

1. **Installation**: Dateien in `custom_components/ade7880` kopieren
2. **Konfiguration**: YAML mit I2C und Sensoren
3. **Deployment**: `esphome run config.yaml`
4. **Verifikation**: Logs prüfen, Sensoren in HA prüfen
5. **Kalibrierung**: Services aufrufen

## 📞 Support

Fragen zur neuen Architektur? Siehe:
- ESPHome Docs: https://esphome.io/components/external_components.html
- Dieser README
- Code-Kommentare in `__init__.py` und `sensor.py`

---

**Version:** 1.0 (2025+ Architektur)
**Status:** ✅ Production Ready
**Lizenz:** MIT
