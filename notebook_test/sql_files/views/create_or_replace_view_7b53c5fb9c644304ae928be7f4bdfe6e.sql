CREATE OR REPLACE VIEW movie_categories AS 
SELECT f.title, c.name 
FROM film f
JOIN category c ON f.category_id = c.category_id;
