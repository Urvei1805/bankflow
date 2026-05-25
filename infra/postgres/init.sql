-- ============================================================
-- BankFlow — PostgreSQL Initialization Script
-- Creates the database and required extensions
-- ============================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE bankflow TO bankflow_user;
