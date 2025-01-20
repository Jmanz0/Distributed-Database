-- DROP DATABASE IF EXISTS region_lookup;
-- DROP DATABASE IF EXISTS category_lookup;
-- DROP DATABASE IF EXISTS temporal_lookup;
-- DROP DATABASE IF EXISTS aid_lookup;

CREATE TABLE IF NOT EXISTS region_lookup (
  region VARCHAR(128) PRIMARY KEY,        -- Region name as a plain string
  keyspace_id VARBINARY(10) NOT NULL      -- Shard identifier
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS category_lookup (
  category VARCHAR(128) PRIMARY KEY,      -- Category name as a plain string
  keyspace_id VARBINARY(10) NOT NULL      -- Shard identifier
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS temporal_lookup (
  temporalGranularity VARCHAR(20) PRIMARY KEY,  -- e.g., daily, weekly, monthly
  keyspace_id VARBINARY(10) NOT NULL            -- Shard identifier
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS aid_lookup (
  aid VARCHAR(128) PRIMARY KEY,           -- Article ID as a plain string
  keyspace_id VARBINARY(10) NOT NULL      -- Shard identifier
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS uid_lookup (
  `uid` VARCHAR(128) PRIMARY KEY,           -- Article ID as a plain string
  keyspace_id VARBINARY(10) NOT NULL      -- Shard identifier
) ENGINE=InnoDB;

-- Populate region_lookup
INSERT INTO region_lookup (region, keyspace_id) VALUES
  ('Beijing', UNHEX('1000000000000000')),   -- 'Beijing' → dbms1
  ('HongKong', UNHEX('9000000000000000'))   -- 'HongKong' → dbms2
ON DUPLICATE KEY UPDATE keyspace_id = VALUES(keyspace_id);

-- Populate category_lookup
INSERT INTO category_lookup (category, keyspace_id) VALUES
  ('science', UNHEX('1000000000000000')),    -- 'science' → dbms1
  ('technology', UNHEX('9000000000000000'))  -- 'technology' → dbms2
ON DUPLICATE KEY UPDATE keyspace_id = VALUES(keyspace_id);

-- Populate temporal_lookup
INSERT INTO temporal_lookup (temporalGranularity, keyspace_id) VALUES
  ('daily', UNHEX('1000000000000000')),    -- 'daily' → dbms1
  ('weekly', UNHEX('9000000000000000')),   -- 'weekly' → dbms2
  ('monthly', UNHEX('9000000000000000'))   -- 'monthly' → dbms2
ON DUPLICATE KEY UPDATE keyspace_id = VALUES(keyspace_id);