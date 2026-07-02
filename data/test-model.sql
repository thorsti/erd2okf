-- 1. MANDANTEN & ORGANISATION (Die Basis-Hierarchie)
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    vat_number VARCHAR(50) UNIQUE,
    settings JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE companies IS 'Zentrale Mandantentabelle. Jedes Asset und jeder User muss einer Company zugeordnet sein.';
COMMENT ON COLUMN companies.settings IS 'Dynamische Konfigurationen wie Feature-Flags oder Custom-Brandings der Company.';


-- 2. BENUTZER & RECHTE (Viele-zu-Viele mit Payload)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT chk_email_format CHECK (email LIKE '%@%.%')
);
COMMENT ON TABLE users IS 'Mitarbeiter der jeweiligen Mandanten.';

CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    permissions TEXT[] NOT NULL
);
COMMENT ON TABLE roles IS 'Globale Rollenprofile mit einer Liste von Berechtigungs-Strings.';

-- Die Brückentabelle mit zusätzlichem Kontext (Zugeordnet von / am)
CREATE TABLE user_roles (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE RESTRICT,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    assigned_by_user_id UUID REFERENCES users(id), -- Selbstreferenzierende Verknüpfung
    PRIMARY KEY (user_id, role_id)
);
COMMENT ON TABLE user_roles IS 'Zuordnungstabelle für Rollen. Enthält Auditing-Metadaten, welcher User die Rolle vergeben hat.';


-- 3. FLOTTENMANAGEMENT & VEHICLES (Hierarchie & Vererbung über Tabellen)
CREATE TABLE vehicle_fleets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    parent_fleet_id UUID REFERENCES vehicle_fleets(id), -- Rekursive Hierarchie (Sub-Flotten)
    name VARCHAR(100) NOT NULL
);
COMMENT ON TABLE vehicle_fleets IS 'Ermöglicht unendlich tief verschachtelte Flottenstrukturen pro Mandant.';

CREATE TABLE vehicles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fleet_id UUID NOT NULL REFERENCES vehicle_fleets(id),
    vin VARCHAR(17) NOT NULL UNIQUE,
    license_plate VARCHAR(20) NOT NULL,
    vehicle_type VARCHAR(50) NOT NULL, -- 'truck', 'drone', 'agv' (Simulation von Polymorphie)
    status VARCHAR(30) DEFAULT 'idle',
    CONSTRAINT chk_vin_length CHECK (LENGTH(vin) = 17)
);
COMMENT ON TABLE vehicles IS 'Stammdaten für Fahrzeuge aller Art. Der Typ bestimmt, welche Sub-Details existieren.';

-- Sub-Typ-Tabelle 1: Spezifisch für LKWs
CREATE TABLE truck_details (
    vehicle_id UUID PRIMARY KEY REFERENCES vehicles(id) ON DELETE CASCADE,
    max_cargo_weight_kg NUMERIC(10, 2) NOT NULL,
    has_trailer BOOLEAN DEFAULT FALSE,
    tachograph_emissions_class VARCHAR(20)
);
COMMENT ON TABLE truck_details IS 'Erweiterte Attribute, falls das Fahrzeug ein LKW ist (1:1 Relation).';

-- Sub-Typ-Tabelle 2: Spezifisch für Lieferdrohnen
CREATE TABLE drone_details (
    vehicle_id UUID PRIMARY KEY REFERENCES vehicles(id) ON DELETE CASCADE,
    battery_capacity_mah INT NOT NULL,
    max_flight_range_meters INT NOT NULL,
    firmware_version VARCHAR(30) NOT NULL
);
COMMENT ON TABLE drone_details IS 'Erweiterte Attribute, falls das Fahrzeug eine Drohne ist (1:1 Relation).';


-- 4. IOT TELEMETRIE-DATEN (Partitionierungs-Kandidat & Time-Series)
CREATE TABLE vehicle_telemetry (
    id BIGSERIAL,
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    gps_coordinates POINT NOT NULL,
    speed_kmh NUMERIC(5,2),
    sensor_payload JSONB NOT NULL, -- Komplexe, verschachtelte Metadaten
    PRIMARY KEY (id, timestamp) -- Verbundener Key, oft genutzt für Time-Series Partitionierung
);
COMMENT ON TABLE vehicle_telemetry IS 'Massen-Telemetriedaten der Fahrzeuge. Extrem hohe Schreiblast.';
COMMENT ON COLUMN vehicle_telemetry.sensor_payload IS 'Beispiel: {"engine_temp_c": 92.5, "tire_pressure_bar": [2.4, 2.4, 2.5, 2.5]}';


-- 5. AUFTRÄGE, ROUTEN & DISPOSITION (Das finale Beziehungs-Chaos)
CREATE TABLE shipments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    tracking_code VARCHAR(100) NOT NULL UNIQUE,
    sender_address JSONB NOT NULL,
    recipient_address JSONB NOT NULL,
    weight_kg NUMERIC(8,2) NOT NULL,
    current_status VARCHAR(50) DEFAULT 'registered'
);
COMMENT ON TABLE shipments IS 'Frachtaufträge, die von den Fahrzeugen transportiert werden.';

-- Die Königsdisziplin für deinen Parser: Eine Route verbindet Fahrzeuge, Schiffe und Zwischenstopps
CREATE TABLE route_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE SET NULL, -- Welches Fahrzeug fährt
    start_time TIMESTAMP WITH TIME ZONE,
    estimated_end_time TIMESTAMP WITH TIME ZONE
);

CREATE TABLE route_stops (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_plan_id UUID NOT NULL REFERENCES route_plans(id) ON DELETE CASCADE,
    shipment_id UUID NOT NULL REFERENCES shipments(id) ON DELETE CASCADE,
    sequence_order INT NOT NULL, -- Reihenfolge des Stopps auf der Route
    stop_type VARCHAR(20) NOT NULL, -- 'pickup', 'dropoff'
    actual_arrival TIMESTAMP WITH TIME ZONE,
    CONSTRAINT uq_route_sequence UNIQUE (route_plan_id, sequence_order)
);
COMMENT ON TABLE route_stops IS 'Verknüpft Routen mit Sendungen. Bestimmt die exakte Reihenfolge von Be- und Entladungen.';