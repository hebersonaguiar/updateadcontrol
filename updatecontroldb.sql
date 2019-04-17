-- CREATE DATABASE updateadcontrol;

--liquibase formatted sql

--changeSet heberson:1

CREATE TABLE IF NOT EXISTS users (
	id INT AUTO_INCREMENT,
	login VARCHAR(255) NOT NULL,
	vinculo VARCHAR(255) NOT NULL,
	cargo VARCHAR(255) NOT NULL,
	departamento VARCHAR(255) NOT NULL,
	sala VARCHAR(255) NOT NULL,
	ramal VARCHAR(255) NOT NULL,
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (id)
) ENGINE=INNODB;

--rollback DROP TABLE updateadcontrol.users;