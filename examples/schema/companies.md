---
type: database-table
title: companies
description: Zentrale Mandantentabelle. Jedes Asset und jeder User muss einer Company
  zugeordnet sein.
okf: 1
table: companies
columns:
- name: id
  type: uuid
  nullable: false
  primary_key: true
- name: name
  type: text
  nullable: false
- name: vat_number
  type: text
  nullable: true
- name: settings
  type: json
  nullable: true
  description: Dynamische Konfigurationen wie Feature-Flags oder Custom-Brandings
    der Company.
- name: created_at
  type: timestamp
  nullable: true
---

Zentrale Mandantentabelle. Jedes Asset und jeder User muss einer Company zugeordnet sein.
