INSERT INTO queries_log (question, description, sql_text, created_at)
VALUES ('Find the id, first name, and last name of an actor from table actor, of whom you know only the first name of "Joe."', 
         'Retrieves the information of the actor with the first name "Joe".', 
         'SELECT a.actor_id, a.first_name, a.last_name FROM actor a WHERE a.first_name = ''Joe''', 
         NOW());
