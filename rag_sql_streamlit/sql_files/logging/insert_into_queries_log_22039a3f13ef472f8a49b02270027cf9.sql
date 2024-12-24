INSERT INTO queries_log (question, description, sql_text, created_at)
VALUES ('Quelle est la liste des films disponibles avec leur catÃ©gorie ?', 'Retrieve a list of available films with their categories', 
'SELECT film.title, category.name FROM film JOIN inventory ON film.film_id = inventory.film_id JOIN rental ON inventory.inventory_id = rental.inventory_id JOIN category ON film.category_id = category.category_id;', NOW());
