INSERT INTO generated_views (view_id, query_id, view_name, created_at)
VALUES (DEFAULT, LAST_INSERT_ID(), 'movie_count', NOW());
