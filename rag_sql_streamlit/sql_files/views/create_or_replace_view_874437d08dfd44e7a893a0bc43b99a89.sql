CREATE OR REPLACE VIEW joe_actor AS
SELECT UPPER(CONCAT(a.first_name, ' ', a.last_name)) AS "Actor Name"
FROM actor a;
