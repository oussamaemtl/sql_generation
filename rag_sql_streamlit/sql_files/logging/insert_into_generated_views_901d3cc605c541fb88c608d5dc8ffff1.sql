INSERT INTO generated_views (view_id, query_id, view_name, created_at)
VALUES 
(NULL, (SELECT MAX(query_id) FROM queries_log) + 1, 'film_count', NOW());
