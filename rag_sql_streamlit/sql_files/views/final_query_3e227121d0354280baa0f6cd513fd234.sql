SELECT a.actor_id, a.first_name, a.last_name
FROM actor a
WHERE tolower(a.last_name) LIKE '%gen%';
