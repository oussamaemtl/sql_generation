INSERT INTO queries_log (query_id, question, description, sql_text, created_at)
VALUES (DEFAULT, 'How many horror movies are there?', 'Count of Horror Movies', 
SELECT COUNT(*) FROM film WHERE film.genre = 'Horror', NOW());
