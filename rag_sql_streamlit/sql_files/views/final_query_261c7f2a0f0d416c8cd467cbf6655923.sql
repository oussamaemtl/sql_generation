SELECT p.title, c.name 
FROM payment_p2007_01 p 
JOIN store s ON p.store_id = s.store_id 
JOIN film_category fc ON s.film_id = fc.film_id 
JOIN category c ON fc.category_id = c.category_id;
