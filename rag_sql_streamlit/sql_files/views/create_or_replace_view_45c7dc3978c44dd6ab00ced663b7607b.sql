CREATE OR REPLACE VIEW Actor_View AS
SELECT UPPER(CONCAT(staff.first_name, ' ', staff.last_name)) AS "Actor Name"
FROM staff;
