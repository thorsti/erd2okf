---
type: database-table
title: vehicle_fleets
description: Ermöglicht unendlich tief verschachtelte Flottenstrukturen pro Mandant.
okf: 1
table: vehicle_fleets
columns:
- name: id
  type: uuid
  nullable: false
  primary_key: true
- name: company_id
  type: uuid
  nullable: false
  references: companies.id
- name: parent_fleet_id
  type: uuid
  nullable: true
  references: vehicle_fleets.id
- name: name
  type: text
  nullable: false
---


