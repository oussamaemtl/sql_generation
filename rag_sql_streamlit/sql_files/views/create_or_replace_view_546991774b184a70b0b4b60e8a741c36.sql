CREATE OR REPLACE VIEW joe_actor AS 
SELECT a.actor_id, a.first_name, a.last_name 
FROM actor a 
WHERE a.first_name = 'Joe';
