INSERT INTO queries_log (question, description, sql_text, created_at)
VALUES ('How many horror movies are there?', 'Count of horror films', 
'SELECT COUNT(*) FROM film WHERE film.genre = ''Horror''', NOW());
