---
okf: 1
table: route_plans
columns:
- name: id
  type: uuid
  nullable: false
  primary_key: true
- name: vehicle_id
  type: uuid
  nullable: true
  references: vehicles.id
- name: start_time
  type: timestamp
  nullable: true
- name: estimated_end_time
  type: timestamp
  nullable: true
---


