INSERT INTO queries_log (question, description, sql_text, created_at)
VALUES ('Find the id, first name, and last name of an actor, of whom you know only the first name of "Joe".', 'Retrieves the details of a specific actor with first name "Joe".', 
         'SELECT staff.staff_id, staff.first_name, staff.last_name 
FROM staff 
WHERE staff.first_name = ''Joe'';', 
         CURRENT_TIMESTAMP);
