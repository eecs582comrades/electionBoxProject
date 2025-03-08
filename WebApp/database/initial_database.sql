-- Name of code artifact: All of them
-- Description: Initial database definition in SQL for the electionbox database.
-- Name(s): William Johnson, Matthew Petillo, Katie Golder
-- Date Created: 3-4-25
-- Dates Revised: 3-4-25
-- Brief description of each revision & author:
-- Revision:


-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS electionbox;

-- Use the database
USE electionbox;

-- Drop the tables if they exist to avoid conflicts during creation
DROP TABLE IF EXISTS `ballots`;

-- Create the `plants` table with FULLTEXT indexes on searchable fields
CREATE TABLE `ballots` (
  `ballot_id` int NOT NULL,
  `barcode_data` text DEFAULT NULL,
  `date` text DEFAULT NULL,
  `time` text DEFAULT NULL,
  `location` text DEFAULT NULL,
  `name` text DEFAULT NULL,
  PRIMARY KEY (`ballot_id`),
  FULLTEXT (`barcode_data`, `date`, `time`, `location`, `name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
