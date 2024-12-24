INSERT INTO queries_log (question, description, sql_text, created_at)
VALUES ('How many films are there ?', 'Counts the number of films in the database.', 'SELECT COUNT(*) FROM film;', NOW());
