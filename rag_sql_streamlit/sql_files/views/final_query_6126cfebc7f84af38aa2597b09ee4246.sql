SELECT f.title, c.name
FROM film_category fc
JOIN films f ON fc.film_id = f.film_id
JOIN categories c ON fc.category_id = c.category_id;
