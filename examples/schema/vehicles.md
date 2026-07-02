---
type: database-table
title: vehicles
description: Stammdaten für Fahrzeuge aller Art. Der Typ bestimmt, welche Sub-Details
  existieren.
okf: 1
table: vehicles
columns:
- name: id
  type: uuid
  nullable: false
  primary_key: true
- name: fleet_id
  type: uuid
  nullable: false
  references: vehicle_fleets.id
- name: vin
  type: text
  nullable: false
- name: license_plate
  type: text
  nullable: false
- name: vehicle_type
  type: text
  nullable: false
- name: status
  type: text
  nullable: true
---

Stammdaten für Fahrzeuge aller Art. Der Typ bestimmt, welche Sub-Details existieren.
