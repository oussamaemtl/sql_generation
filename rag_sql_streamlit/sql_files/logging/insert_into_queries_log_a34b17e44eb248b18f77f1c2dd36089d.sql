INSERT INTO queries_log (question, description, sql_text, created_at)
VALUES ('Quelle est la liste des films disponibles avec leur catÃ©gorie ?', 'Retrieve film titles and categories', 
         'SELECT a.title, b.category FROM film a JOIN film_category b ON a.film_id = b.film_id;', NOW());
