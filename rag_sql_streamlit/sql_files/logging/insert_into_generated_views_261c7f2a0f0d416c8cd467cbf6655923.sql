INSERT INTO generated_views (view_id, query_id, view_name, created_at)
VALUES ((SELECT COALESCE(MAX(view_id), 0) + 1 FROM generated_views), 
        (SELECT query_id FROM queries_log WHERE question = 'Quelle est la liste des films disponibles avec leur catÃ©gorie ?',), 
        'available_films', NOW());
