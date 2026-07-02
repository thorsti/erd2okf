---
type: database-table
title: users
description: Mitarbeiter der jeweiligen Mandanten.
okf: 1
table: users
columns:
- name: id
  type: uuid
  nullable: false
  primary_key: true
- name: company_id
  type: uuid
  nullable: false
  references: companies.id
- name: email
  type: text
  nullable: false
- name: password_hash
  type: text
  nullable: false
- name: is_active
  type: boolean
  nullable: true
---


