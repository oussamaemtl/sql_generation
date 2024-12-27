INSERT INTO queries_log (question, description, sql_text, created_at)
VALUES ('Create a list of all the actorsâ€™ first name and last name. Display the first and last name of each actor in a single column in upper case letters. Name the column Actor Name.', 
         'Retrieves the names of all actors, formatting them as "Actor Name".', 
         'SELECT UPPER(CONCAT(a.first_name, '' , a.last_name)) AS ''Actor Name'' FROM actor a;', 
         NOW());
