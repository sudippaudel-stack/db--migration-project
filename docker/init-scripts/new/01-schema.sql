CREATE DATABASE IF NOT EXISTS new_db;
USE new_db;

DROP TABLE IF EXISTS beneficiary;

CREATE TABLE beneficiary (
  beneficiary_id   VARCHAR(20)  PRIMARY KEY,
  party_role_id    VARCHAR(20),
  first_name       VARCHAR(100),
  last_name        VARCHAR(100),
  lkp_relation_id  VARCHAR(20),
  ssn              TEXT,
  dob              DATE,
  ssn4             VARCHAR(4),
  middle_name      VARCHAR(100),
  is_primary       BOOL,
  percentage       FLOAT,
  created_at       BIGINT,
  updated_at       BIGINT,
  deleted_at       BIGINT,
  is_contigent     BOOL
);
