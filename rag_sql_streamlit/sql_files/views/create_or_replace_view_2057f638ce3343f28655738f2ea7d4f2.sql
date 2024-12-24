CREATE OR REPLACE VIEW Horror_Movies AS
SELECT COUNT(*)
FROM film
WHERE film.genre = 'Horror';
