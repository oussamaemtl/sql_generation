CREATE OR REPLACE VIEW joe_actors AS 
SELECT staff.staff_id, staff.first_name, staff.last_name
FROM staff
WHERE staff.first_name = 'Joe';
