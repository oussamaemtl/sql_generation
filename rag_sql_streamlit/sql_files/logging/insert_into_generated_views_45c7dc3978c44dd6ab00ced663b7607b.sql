INSERT INTO generated_views (view_id, query_id, view_name, created_at)
VALUES ((SELECT MAX(view_id) + 1 FROM generated_views), 1, 'Actor_View', NOW());
