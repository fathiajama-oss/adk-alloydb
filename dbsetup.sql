-- DDL for the 'benefits' table
CREATE TABLE IF NOT EXISTS benefits (
    employee_id VARCHAR(10) PRIMARY KEY,
    plan_name VARCHAR(100) NOT NULL,
    individual_deductible NUMERIC(10, 2) NOT NULL,
    individual_oop_max NUMERIC(10, 2) NOT NULL,
    hsa_eligible BOOLEAN,
    last_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- DDL for the 'providers' table
CREATE TABLE IF NOT EXISTS providers (
    provider_id SERIAL PRIMARY KEY,
    provider_name VARCHAR(100) NOT NULL,
    specialty VARCHAR(50) NOT NULL,
    network_status VARCHAR(20) NOT NULL,
    location VARCHAR(100)
);

-- -----------------------------------------------------------------------------
-- Mock Data Insertion
-- -----------------------------------------------------------------------------

-- Insert data into 'benefits'
-- Employee ID 123 (used in the example query) will have a low deductible (Challenge 4 alert condition)
INSERT INTO benefits (employee_id, plan_name, individual_deductible, individual_oop_max, hsa_eligible) VALUES
('101', 'Benifix Platinum PPO', 1000.00, 5000.00, TRUE),
('123', 'Benifix Bronze HMO', 450.00, 6500.00, FALSE),
('456', 'Benifix Gold PPO', 2500.00, 3000.00, TRUE),
('789', 'Benifix Essential', 5000.00, 8000.00, FALSE);

-- Insert data into 'providers'
INSERT INTO providers (provider_name, specialty, network_status, location) VALUES
('Dr. Alice Smith', 'DENTIST', 'IN_NETWORK', '123 Main St, Anytown'),
('Acme Dental Group', 'DENTIST', 'IN_NETWORK', '456 Oak Ave, Anytown'),
('Dr. Bob Johnson', 'PHYSICIAN', 'IN_NETWORK', '789 Pine Ln, Anytown'),
('City Orthopedics', 'ORTHOPEDIC', 'IN_NETWORK', '101 Elm Blvd, Anytown'),
('Dr. Carol Davis', 'PEDIATRICIAN', 'OUT_OF_NETWORK', '202 Maple Dr, Anytown'),
('Ancillary Services', 'CHIROPRACTOR', 'IN_NETWORK', '303 Birch Ct, Anytown');

-- DDL for the 'policy_documents' table (Challenge 2)
-- Requires the 'vector' extension to be enabled in AlloyDB for PostgreSQL.
-- CREATE EXTENSION vector; 

CREATE TABLE IF NOT EXISTS policy_documents (
    policy_id SERIAL PRIMARY KEY,
    chunk_text TEXT NOT NULL
);