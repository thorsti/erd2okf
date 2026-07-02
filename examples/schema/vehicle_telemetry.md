---
okf: 1
table: vehicle_telemetry
columns:
- name: id
  type: integer
  nullable: false
  primary_key: true
- name: vehicle_id
  type: uuid
  nullable: false
  references: vehicles.id
- name: timestamp
  type: timestamp
  nullable: false
  primary_key: true
- name: gps_coordinates
  type: point
  nullable: false
- name: speed_kmh
  type: numeric
  nullable: true
- name: sensor_payload
  type: json
  nullable: false
  description: 'Beispiel: {"engine_temp_c": 92.5, "tire_pressure_bar": [2.4, 2.4,
    2.5, 2.5]}'
---

Massen-Telemetriedaten der Fahrzeuge. Extrem hohe Schreiblast.
