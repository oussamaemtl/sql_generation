INSERT INTO generated_views (view_id, query_id, view_name, created_at)
VALUES ((SELECT COALESCE(MAX(view_id), 0) FROM generated_views) + 1, 
        (SELECT MAX(query_id) FROM queries_log), 'available_films', NOW());
