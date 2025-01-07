INSERT INTO queries_log (question, description, sql_text, created_at)
VALUES 
('Give me the total number of films', 'Retrieves the total number of films.', 
'SELECT COUNT(*) FROM film;', NOW());
