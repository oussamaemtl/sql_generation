CREATE OR REPLACE VIEW movie_count AS 
SELECT COUNT(*) 
FROM film 
WHERE film.title IS NOT NULL;