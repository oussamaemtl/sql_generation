INSERT INTO queries_log (question, description, sql_text, created_at)
VALUES ('Find all actors whose last name contain the letters GEN. Make this case insensitive', 'Retrieves actors whose last name contains "GEN" (case-insensitive).', 'SELECT a.actor_id, a.first_name, a.last_name FROM actor a WHERE tolower(a.last_name) LIKE ''%gen'''', NOW());
