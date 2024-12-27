INSERT INTO queries_log (question, description, sql_text, created_at)
VALUES ('Montre moi tous les films qui ont un acteur qui s''appelle "JOE"', 'Retrieves the information of films with an actor named "Joe".', 
'SELECT f.title, a.first_name, a.last_name FROM film f JOIN actor a ON f.actor_id = a.actor_id WHERE a.first_name = ''Joe'', NOW());
