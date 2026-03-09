CREATE DATABASE IF NOT EXISTS legacy_db;
USE legacy_db;

DROP TABLE IF EXISTS dependents;

CREATE TABLE dependents (
    `did`                  INT              NOT NULL AUTO_INCREMENT,
    `userid`               INT              NOT NULL,
    `d_fname`              VARCHAR(225)     DEFAULT NULL,
    `d_lname`              VARCHAR(225)     DEFAULT NULL,
    `d_mname`              VARCHAR(10)      DEFAULT NULL,
    `d_relate`             VARCHAR(10)      DEFAULT NULL,
    `d_gender`             VARCHAR(1)       DEFAULT NULL,
    `d_ssn`                VARCHAR(100)     DEFAULT NULL,
    `d_dob`                VARCHAR(225)     DEFAULT NULL,
    `d_ssn4`               VARCHAR(10)      DEFAULT NULL,
    `additional_notes`     TEXT             DEFAULT NULL,
    `disabled`             VARCHAR(1)       DEFAULT '0',
    `dhrq`                 VARCHAR(10)      DEFAULT NULL,
    `dhrq2`                VARCHAR(10)      DEFAULT NULL,
    `dwrq`                 VARCHAR(10)      DEFAULT NULL,
    `is_approved`          VARCHAR(1)       DEFAULT '0',
    `created_at`           TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`           TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted_at`           TIMESTAMP        DEFAULT NULL,
    `is_legally_disabled`  TINYINT(1)       DEFAULT 0,
    `disability_condition` VARCHAR(255)     DEFAULT NULL,
    PRIMARY KEY (`did`),
    INDEX `idx_dependents_userid`     (`userid`),
    INDEX `idx_dependents_deleted_at` (`deleted_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
