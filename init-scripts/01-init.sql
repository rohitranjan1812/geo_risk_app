-- Initialize georisk database
-- This script runs automatically when the database container first starts

-- Ensure the database exists
SELECT 'CREATE DATABASE georisk_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'georisk_db')\gexec

-- Connect to the database
\c georisk_db

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE georisk_db TO georisk;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Database initialization complete';
END $$;
