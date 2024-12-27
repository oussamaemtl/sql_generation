INSERT INTO queries_log (question, description, sql_text, created_at)
VALUES ('Find all actors whose last name contain the letters GEN. Make this case insensitive.', 'Retrieves all actors whose last name contains the letters GEN, ignoring case.', 'SELECT * FROM actor WHERE UPPER(last_name) LIKE ''%GEN%'', ', NOW());
