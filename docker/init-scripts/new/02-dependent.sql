CREATE DATABASE IF NOT EXISTS new_db;
USE new_db;

DROP TABLE IF EXISTS dependent;

CREATE TABLE dependent (
    `dependent_id`           VARCHAR(20)      NOT NULL,
    `party_role_id`          VARCHAR(20)      NOT NULL,
    `first_name`             VARCHAR(100)     DEFAULT NULL,
    `last_name`              VARCHAR(100)     DEFAULT NULL,
    `middle_name`            VARCHAR(100)     DEFAULT NULL,
    `lkp_relation_id`        VARCHAR(20)      DEFAULT NULL,
    `lkp_gender_id`          VARCHAR(20)      DEFAULT NULL,
    `ssn`                    TEXT             DEFAULT NULL,
    `dob`                    DATE             DEFAULT NULL,
    `ssn4`                   VARCHAR(4)       DEFAULT NULL,
    `notes`                  TEXT             DEFAULT NULL,
    `is_disabled`            BOOLEAN          DEFAULT FALSE,
    `height_in_feet`         INT              DEFAULT NULL,
    `height_in_inch`         INT              DEFAULT NULL,
    `weight`                 FLOAT            DEFAULT NULL,
    `is_approved`            BOOLEAN          DEFAULT FALSE,
    `created_at`             BIGINT           DEFAULT NULL,
    `updated_at`             BIGINT           DEFAULT NULL,
    `deleted_at`             BIGINT           DEFAULT NULL,
    `is_legally_disapproved` BOOLEAN          DEFAULT FALSE,
    `disability_condition`   VARCHAR(255)     DEFAULT NULL,
    PRIMARY KEY (`dependent_id`),
    INDEX `idx_dependent_party_role_id`   (`party_role_id`),
    INDEX `idx_dependent_deleted_at`      (`deleted_at`),
    INDEX `idx_dependent_lkp_relation_id` (`lkp_relation_id`),
    INDEX `idx_dependent_lkp_gender_id`   (`lkp_gender_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
