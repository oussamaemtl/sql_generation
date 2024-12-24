INSERT INTO generated_views (view_id, query_id, view_name, created_at)
VALUES ((SELECT COALESCE(MAX(view_id), 0) + 1 FROM generated_views), 
        (SELECT query_id FROM queries_log ORDER BY query_id DESC LIMIT 1), 'horror_movies', NOW());
