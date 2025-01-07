CREATE OR REPLACE VIEW actor_names AS
SELECT UPPER(CONCAT(a.first_name, ' ', a.last_name)) AS 'Actor Name'
FROM actor a;
