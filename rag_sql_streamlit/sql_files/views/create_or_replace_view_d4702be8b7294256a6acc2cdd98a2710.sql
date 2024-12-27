CREATE OR REPLACE VIEW find_gen_actors AS
SELECT *
FROM actor
WHERE UPPER(last_name) LIKE '%GEN%';
