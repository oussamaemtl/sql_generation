INSERT INTO queries_log (question, description, sql_text, created_at)
VALUES ('Quelle est la liste des films disponibles avec leur catégorie ?', 'List of available movies with their categories', 'SELECT f.title, c.name FROM film f JOIN category c ON f.category_id = c.category_id;', NOW());
