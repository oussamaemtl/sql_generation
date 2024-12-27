CREATE OR REPLACE VIEW joe_films AS
SELECT f.title, a.first_name, a.last_name 
FROM film f 
JOIN actor a ON f.actor_id = a.actor_id 
WHERE a.first_name = 'Joe';
