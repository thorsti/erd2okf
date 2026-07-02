---
type: database-table
title: truck_details
description: Erweiterte Attribute, falls das Fahrzeug ein LKW ist (1:1 Relation).
okf: 1
table: truck_details
columns:
- name: vehicle_id
  type: uuid
  nullable: false
  primary_key: true
  references: vehicles.id
- name: max_cargo_weight_kg
  type: numeric
  nullable: false
- name: has_trailer
  type: boolean
  nullable: true
- name: tachograph_emissions_class
  type: text
  nullable: true
---

Erweiterte Attribute, falls das Fahrzeug ein LKW ist (1:1 Relation).
