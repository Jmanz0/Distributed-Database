DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS article;
DROP TABLE IF EXISTS `read`;
DROP TABLE IF EXISTS be_read;
DROP TABLE IF EXISTS popular_rank;
-- User table
CREATE TABLE IF NOT EXISTS user (
  id BIGINT PRIMARY KEY,
  timestamp VARCHAR(20),
  uid INT UNIQUE,
  name VARCHAR(100),
  gender VARCHAR(10),
  email VARCHAR(100),
  phone VARCHAR(20),
  dept VARCHAR(100),
  grade VARCHAR(50),
  language VARCHAR(50),
  region VARCHAR(50),
  role VARCHAR(50),
  preferTags TEXT,
  obtainedCredits INT
);

-- Article table
CREATE TABLE IF NOT EXISTS article (
  id BIGINT PRIMARY KEY,
  timestamp VARCHAR(20),
  aid INT UNIQUE,
  title VARCHAR(200),
  category VARCHAR(50),
  abstract TEXT,
  articleTags TEXT,
  authors TEXT,
  language VARCHAR(50),
  text TEXT,
  image BLOB,
  video BLOB
);

-- Read table
CREATE TABLE IF NOT EXISTS `read` (
  id BIGINT PRIMARY KEY,
  timestamp VARCHAR(20),
  uid INT,
  aid INT,
  readTimeLength INT,
  agreeOrNot BOOLEAN,
  commentOrNot BOOLEAN,
  commentDetail TEXT,
  shareOrNot BOOLEAN
);

-- Be-Read table
CREATE TABLE IF NOT EXISTS be_read (
  id BIGINT PRIMARY KEY,
  timestamp VARCHAR(20),
  aid INT,
  readNum INT,
  readUidList TEXT,
  commentNum INT,
  commentUidList TEXT,
  agreeNum INT,
  agreeUidList TEXT,
  shareNum INT,
  shareUidList TEXT,
  category VARCHAR(50)
);

-- Popular-Rank table
CREATE TABLE IF NOT EXISTS popular_rank (
  id BIGINT PRIMARY KEY,
  timestamp VARCHAR(20),
  temporalGranularity VARCHAR(50),
  articleAidList TEXT
);

ALTER TABLE article ADD COLUMN processed BOOLEAN DEFAULT FALSE NULL;
ALTER TABLE user ADD COLUMN processed BOOLEAN DEFAULT FALSE NULL;

ALTER TABLE article ADD COLUMN processed_duplicate BOOLEAN DEFAULT FALSE;
ALTER TABLE be_read ADD COLUMN processed_duplicate BOOLEAN DEFAULT FALSE;