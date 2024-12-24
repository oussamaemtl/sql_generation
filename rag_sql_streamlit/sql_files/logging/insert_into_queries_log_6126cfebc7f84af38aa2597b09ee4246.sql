INSERT INTO queries_log (question, description, sql_text, created_at)
VALUES ('Quelle est la liste des films disponibles avec leur catÃ©gorie ?', 'List of available films with their category', 
        'SELECT f.title, c.name
         FROM film_category fc
         JOIN films f ON fc.film_id = f.film_id
         JOIN categories c ON fc.category_id = c.category_id;', NOW());
