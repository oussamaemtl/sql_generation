INSERT INTO queries_log (question, description, sql_text, created_at)
VALUES ('How many movies are they ?', 'Number of movies', 'SELECT COUNT(*) FROM film WHERE film.title IS NOT NULL;', NOW());
