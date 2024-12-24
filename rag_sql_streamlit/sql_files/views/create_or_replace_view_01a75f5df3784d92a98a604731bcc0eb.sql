CREATE OR REPLACE VIEW joe_actor AS 
SELECT staff_id, first_name, last_name 
FROM staff 
WHERE first_name = 'Joe';
