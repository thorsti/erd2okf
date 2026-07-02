---
type: database-schema
title: postgres
description: 'Generierter OKF-Snapshot eines Datenbankschemas: 12 Tabellen.'
okf: 1
---

<!-- Von erd2okf generiert. Hand-Edits gehen bei der nächsten Generierung
     verloren — Semantik gehört in den Body der Tabellen-Files. -->

# postgres

| Tabelle | Beschreibung |
| --- | --- |
| [companies](./companies.md) | Zentrale Mandantentabelle. Jedes Asset und jeder User muss einer Company zugeordnet sein. |
| [drone_details](./drone_details.md) | Erweiterte Attribute, falls das Fahrzeug eine Drohne ist (1:1 Relation). |
| [roles](./roles.md) | Globale Rollenprofile mit einer Liste von Berechtigungs-Strings. |
| [route_plans](./route_plans.md) |  |
| [route_stops](./route_stops.md) | Verknüpft Routen mit Sendungen. Bestimmt die exakte Reihenfolge von Be- und Entladungen. |
| [shipments](./shipments.md) | Frachtaufträge, die von den Fahrzeugen transportiert werden. |
| [truck_details](./truck_details.md) | Erweiterte Attribute, falls das Fahrzeug ein LKW ist (1:1 Relation). |
| [user_roles](./user_roles.md) | Zuordnungstabelle für Rollen. Enthält Auditing-Metadaten, welcher User die Rolle vergeben hat. |
| [users](./users.md) | Mitarbeiter der jeweiligen Mandanten. |
| [vehicle_fleets](./vehicle_fleets.md) | Ermöglicht unendlich tief verschachtelte Flottenstrukturen pro Mandant. |
| [vehicle_telemetry](./vehicle_telemetry.md) | Massen-Telemetriedaten der Fahrzeuge. Extrem hohe Schreiblast. |
| [vehicles](./vehicles.md) | Stammdaten für Fahrzeuge aller Art. Der Typ bestimmt, welche Sub-Details existieren. |

## ERD

```mermaid
erDiagram
    companies {
        uuid id PK
        text name
        text vat_number
        json settings
        timestamp created_at
    }
    drone_details {
        uuid vehicle_id PK, FK
        integer battery_capacity_mah
        integer max_flight_range_meters
        text firmware_version
    }
    roles {
        uuid id PK
        text name
        array permissions
    }
    route_plans {
        uuid id PK
        uuid vehicle_id FK
        timestamp start_time
        timestamp estimated_end_time
    }
    route_stops {
        uuid id PK
        uuid route_plan_id FK
        uuid shipment_id FK
        integer sequence_order
        text stop_type
        timestamp actual_arrival
    }
    shipments {
        uuid id PK
        uuid company_id FK
        text tracking_code
        json sender_address
        json recipient_address
        numeric weight_kg
        text current_status
    }
    truck_details {
        uuid vehicle_id PK, FK
        numeric max_cargo_weight_kg
        boolean has_trailer
        text tachograph_emissions_class
    }
    user_roles {
        uuid user_id PK, FK
        uuid role_id PK, FK
        timestamp assigned_at
        uuid assigned_by_user_id FK
    }
    users {
        uuid id PK
        uuid company_id FK
        text email
        text password_hash
        boolean is_active
    }
    vehicle_fleets {
        uuid id PK
        uuid company_id FK
        uuid parent_fleet_id FK
        text name
    }
    vehicle_telemetry {
        integer id PK
        uuid vehicle_id FK
        timestamp timestamp PK
        point gps_coordinates
        numeric speed_kmh
        json sensor_payload
    }
    vehicles {
        uuid id PK
        uuid fleet_id FK
        text vin
        text license_plate
        text vehicle_type
        text status
    }
    drone_details |o--|| vehicles : "vehicle_id"
    route_plans }o--|| vehicles : "vehicle_id"
    route_stops }o--|| route_plans : "route_plan_id"
    route_stops }o--|| shipments : "shipment_id"
    shipments }o--|| companies : "company_id"
    truck_details |o--|| vehicles : "vehicle_id"
    user_roles }o--|| users : "user_id"
    user_roles }o--|| roles : "role_id"
    user_roles }o--|| users : "assigned_by_user_id"
    users }o--|| companies : "company_id"
    vehicle_fleets }o--|| companies : "company_id"
    vehicle_fleets }o--|| vehicle_fleets : "parent_fleet_id"
    vehicle_telemetry }o--|| vehicles : "vehicle_id"
    vehicles }o--|| vehicle_fleets : "fleet_id"
```
