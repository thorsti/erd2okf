---
type: database-table
title: user_roles
description: Zuordnungstabelle für Rollen. Enthält Auditing-Metadaten, welcher User
  die Rolle vergeben hat.
okf: 1
table: user_roles
columns:
- name: user_id
  type: uuid
  nullable: false
  primary_key: true
  references: users.id
- name: role_id
  type: uuid
  nullable: false
  primary_key: true
  references: roles.id
- name: assigned_at
  type: timestamp
  nullable: true
- name: assigned_by_user_id
  type: uuid
  nullable: true
  references: users.id
---

Zuordnungstabelle für Rollen. Enthält Auditing-Metadaten, welcher User die Rolle vergeben hat.
