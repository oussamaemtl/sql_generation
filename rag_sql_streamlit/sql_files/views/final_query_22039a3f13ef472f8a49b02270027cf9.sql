SELECT film.title, category.name
FROM film
JOIN inventory ON film.film_id = inventory.film_id
JOIN rental ON inventory.inventory_id = rental.inventory_id
JOIN category ON film.category_id = category.category_id;
