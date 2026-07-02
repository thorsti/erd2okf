---
type: database-table
title: route_stops
description: Verknüpft Routen mit Sendungen. Bestimmt die exakte Reihenfolge von Be-
  und Entladungen.
okf: 1
table: route_stops
columns:
- name: id
  type: uuid
  nullable: false
  primary_key: true
- name: route_plan_id
  type: uuid
  nullable: false
  references: route_plans.id
- name: shipment_id
  type: uuid
  nullable: false
  references: shipments.id
- name: sequence_order
  type: integer
  nullable: false
- name: stop_type
  type: text
  nullable: false
- name: actual_arrival
  type: timestamp
  nullable: true
---

Verknüpft Routen mit Sendungen. Bestimmt die exakte Reihenfolge von Be- und Entladungen.
