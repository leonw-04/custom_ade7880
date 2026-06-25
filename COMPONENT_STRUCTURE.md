# 🏗️ ESPHome ADE7880 Component - Korrekte External Component Struktur (2025+)

## ✅ Verzeichnisstruktur (Standard)

```
custom_ade7880/                          ← Dieses Repository
├── components/                          ← Root für alle Components
│   └── ade7880/                         ← Eine Component
│       ├── __init__.py                  ← Haupt-Config + Codegen
│       ├── sensor.py                    ← Sensor-Plattform
│       ├── ade7880_calibration.h        ← C++ Header
│       └── ade7880_calibration.cpp      ← C++ Implementation
│
├── LICENSE
├── README.md                            ← Projekt-Dokumentation
├── INTEGRATION_TUTORIAL.md
├── EXTERNAL_COMPONENT_GUIDE.md
└── ... (weitere Docs)
```

## 🎯 So wird das Repository in Projekten eingebunden

### Option 1: Lokal (für Entwicklung)

```
my_esphome_project/
├── config.yaml
└── custom_components/
    └── ade7880/                        ← Symlink zu components/ade7880
```

**Kopieren:**
```bash
mkdir -p my_esphome_project/custom_components
cp -r custom_ade7880/components/ade7880 my_esphome_project/custom_components/
```

**YAML:**
```yaml
external_components:
  - source:
      type: local
      path: ./custom_components/ade7880
    components: [ade7880]
```

### Option 2: Aus Git Repository

**YAML:**
```yaml
external_components:
  - source:
      github: leonw-04/custom_ade7880@main
      path: components/ade7880
    components: [ade7880]
```

ESPHome lädt dann automatisch aus: `https://github.com/leonw-04/custom_ade7880/blob/main/components/ade7880/`

## 📋 Warum diese Struktur?

| Ordner | Zweck | ESPHome lädt |
|--------|-------|-------------|
| `components/ade7880/` | Eine Component | Ja ✓ |
| `components/ade7880/__init__.py` | Hauptkomponente | `.namespace()`, `.class_()` |
| `components/ade7880/sensor.py` | Sensor-Plattform | `.sensor_schema()` |
| `.h` / `.cpp` | C++ Firmware-Code | Via Namespace |

## 🚀 Minimale YAML zum Testen

```yaml
esphome:
  name: test-ade7880
  platform: ESP32
  board: esp32dev

i2c:
  sda: GPIO21
  scl: GPIO22

external_components:
  - source:
      type: local
      path: ./custom_components/ade7880
    components: [ade7880]

sensor:
  - platform: ade7880
    voltage_a:
      name: "Voltage A"
```

## ✅ Validierung der Struktur

Diese Component ist **Production-Ready** mit:

- ✅ Korrekte Verzeichnisstruktur (`components/ade7880/`)
- ✅ `__init__.py` mit `CONFIG_SCHEMA` und `to_code()`
- ✅ `sensor.py` mit Sensor-Plattformdefinition
- ✅ C++ Header & Implementation mit Namespaces
- ✅ Alle 9 Messwert-Register (V, I, P × 3 Phasen)
- ✅ Alle 9 Gain-Register (Kalibrierungs-Faktoren)
- ✅ ESPPreferences für persistente Speicherung
- ✅ Home Assistant Services
- ✅ Vollständige Dokumentation

## 📚 Dokumentation

| Datei | Für wen | Inhalt |
|-------|---------|--------|
| **README.md** | Entwickler | Übersicht & Installation |
| **INTEGRATION_TUTORIAL.md** | Anfänger | Schritt-für-Schritt Anleitung |
| **EXTERNAL_COMPONENT_GUIDE.md** | Architektur-Interessierte | Wie die neue Struktur funktioniert |
| **IMPLEMENTATION_NOTES.md** | Deep-Dive | Register, Mathematik, I2C |
| **VALIDATION.md** | QA | Checklisten & Tests |
| **QUICKSTART.md** | Schnellstart | 3-Schritte Setup |

## 🔧 Verwendung in Ihrem Projekt

### Schritt 1: Komponente kopieren

```bash
cd my_esphome_project
mkdir -p custom_components
cp -r ../custom_ade7880/components/ade7880 custom_components/
```

### Schritt 2: YAML konfigurieren

```yaml
external_components:
  - source:
      type: local
      path: ./custom_components/ade7880
    components: [ade7880]

i2c:
  sda: GPIO21
  scl: GPIO22
  frequency: 100kHz

sensor:
  - platform: ade7880
    voltage_a: {name: "Voltage A"}
    current_a: {name: "Current A"}
    power_a: {name: "Power A"}
```

### Schritt 3: Deployment

```bash
esphome run config.yaml --device /dev/ttyUSB0
```

## 📊 Was die Komponente kann

### Messwerte (9 Kanäle, alle optional)

```
Phase A, B, C:
  • Spannung RMS (VRMS) in Volt
  • Strom RMS (IRMS) in Ampere
  • Wirkleistung (WATT) in Watt
```

### Kalibrierung (Home Assistant Services)

```yaml
service: ade7880.calibrate_voltage
data:
  phase: "A"
  target_voltage: 230.5

service: ade7880.calibrate_current
data:
  phase: "A"
  target_current: 10.5

service: ade7880.calibrate_power
data:
  phase: "A"
  target_power: 2415.0

service: ade7880.reset_calibration
```

### Persistenz

- Kalibrierungs-Werte werden in Flash gespeichert
- Automatisches Laden beim Boot
- Überleben von Neustarts und OTA-Updates

## 🎯 Production-Checklist

- [x] Struktur: `components/ade7880/`
- [x] `__init__.py` mit CONFIG_SCHEMA
- [x] `sensor.py` mit Sensor-Integration
- [x] C++ Header & Implementation
- [x] Alle Register implementiert
- [x] I2C Big-Endian korrekt
- [x] 24-Bit Sign-Extension
- [x] Kalibrierungs-Mathematik
- [x] ESPPreferences Persistenz
- [x] HA Services
- [x] Dokumentation vollständig
- [x] Tests validiert

## 🌐 Repository Links

- **GitHub:** https://github.com/leonw-04/custom_ade7880
- **Branch:** main
- **Komponenten-Pfad:** components/ade7880/

## 📞 Support

Fragen? Siehe:
- **INTEGRATION_TUTORIAL.md** für Installation
- **EXTERNAL_COMPONENT_GUIDE.md** für Architektur
- **IMPLEMENTATION_NOTES.md** für Technisches

---

**Status:** ✅ PRODUCTION READY
**Architektur:** ESPHome 2025+ External Component Standard
**Version:** 1.0
**Lizenz:** MIT
