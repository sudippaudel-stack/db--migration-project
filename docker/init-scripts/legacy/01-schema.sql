CREATE DATABASE IF NOT EXISTS legacy_db;
USE legacy_db;

DROP TABLE IF EXISTS beneficiary;

CREATE TABLE beneficiary (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  userid         INT,
  fname          VARCHAR(255),
  lname          VARCHAR(255),
  relation       VARCHAR(255),
  ssn            VARCHAR(255),
  dob            VARCHAR(255),
  ssn4           VARCHAR(5),
  mname          VARCHAR(255),
  is_primary     INT DEFAULT 0,
  ben_percentage VARCHAR(3),
  created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  deleted_at     TIMESTAMP NULL,
  is_contigent   TINYINT DEFAULT 0
);

INSERT INTO beneficiary
  (userid, fname, lname, relation, ssn, dob, ssn4, mname, is_primary, ben_percentage, deleted_at, is_contigent)
VALUES
  (101, 'John',   'Doe',     'SPOUSE',  '123456789', '1985-03-22', '6789', 'A',       1, '50',  NULL,        0),
  (102, 'Jane',   'Smith',   'CHILD',   '987654321', '2005-07-14', '4321', 'B',       0, '25',  NULL,        0),
  (103, 'Robert', 'Johnson', 'PARENT',  '456789123', '1960-11-05', '9123', 'C',       0, '25',  NULL,        1),
  (104, 'Emily',  'Davis',   'SIBLING', '321654987', '1990-01-30', '4987', NULL,      0, '100', NOW(),       0),
  (105, 'Michael','Wilson',  'OTHER',   '654321789', '1975-08-19', '1789', 'D',       1, '75',  NULL,        0);
