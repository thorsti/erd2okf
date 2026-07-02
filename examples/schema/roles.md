---
type: database-table
title: roles
description: Globale Rollenprofile mit einer Liste von Berechtigungs-Strings.
okf: 1
table: roles
columns:
- name: id
  type: uuid
  nullable: false
  primary_key: true
- name: name
  type: text
  nullable: false
- name: permissions
  type: array
  nullable: false
---


