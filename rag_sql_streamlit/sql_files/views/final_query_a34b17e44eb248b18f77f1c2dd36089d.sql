SELECT a.title, b.category 
FROM film a
JOIN film_category b ON a.film_id = b.film_id;
