---
type: database-table
title: shipments
description: Frachtaufträge, die von den Fahrzeugen transportiert werden.
okf: 1
table: shipments
columns:
- name: id
  type: uuid
  nullable: false
  primary_key: true
- name: company_id
  type: uuid
  nullable: false
  references: companies.id
- name: tracking_code
  type: text
  nullable: false
- name: sender_address
  type: json
  nullable: false
- name: recipient_address
  type: json
  nullable: false
- name: weight_kg
  type: numeric
  nullable: false
- name: current_status
  type: text
  nullable: true
---

Frachtaufträge, die von den Fahrzeugen transportiert werden.
