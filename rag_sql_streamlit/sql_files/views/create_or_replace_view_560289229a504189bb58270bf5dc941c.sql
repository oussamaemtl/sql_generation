CREATE OR REPLACE VIEW horror_movies AS
SELECT COUNT(*)
FROM film
WHERE film.genre = 'Horror';
