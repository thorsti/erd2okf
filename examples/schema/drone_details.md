---
type: database-table
title: drone_details
description: Erweiterte Attribute, falls das Fahrzeug eine Drohne ist (1:1 Relation).
okf: 1
table: drone_details
columns:
- name: vehicle_id
  type: uuid
  nullable: false
  primary_key: true
  references: vehicles.id
- name: battery_capacity_mah
  type: integer
  nullable: false
- name: max_flight_range_meters
  type: integer
  nullable: false
- name: firmware_version
  type: text
  nullable: false
---

Erweiterte Attribute, falls das Fahrzeug eine Drohne ist (1:1 Relation).
