CREATE ROLE reg_service WITH LOGIN PASSWORD '123';
CREATE DATABASE reg_service_db;
GRANT CONNECT, CREATE ON DATABASE reg_service_db TO reg_service;
\c reg_service_db
GRANT USAGE, CREATE ON SCHEMA PUBLIC TO reg_service;