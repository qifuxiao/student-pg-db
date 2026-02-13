-- 强制密码认证
CREATE USER student_app WITH PASSWORD 'student_secure_pass';

CREATE DATABASE student_management
    OWNER student_app
    ENCODING 'UTF8';

GRANT ALL PRIVILEGES ON DATABASE student_management TO student_app;

ALTER ROLE student_app SET client_encoding TO 'utf8';
ALTER ROLE student_app SET default_transaction_isolation TO 'read committed';
ALTER ROLE student_app SET timezone TO 'Asia/Shanghai';
