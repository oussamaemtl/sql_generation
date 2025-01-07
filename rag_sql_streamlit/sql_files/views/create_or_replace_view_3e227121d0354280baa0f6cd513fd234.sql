CREATE OR REPLACE VIEW actors_with_gen AS
SELECT a.actor_id, a.first_name, a.last_name
FROM actor a
WHERE tolower(a.last_name) LIKE '%gen%';
