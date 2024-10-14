DROP PROCEDURE IF EXISTS insert_default_states_cases;
DROP PROCEDURE IF EXISTS insert_default_states_damage;



CREATE PROCEDURE insert_default_states_cases()
BEGIN
    INSERT IGNORE INTO states_cases (id, name, is_deleted, created_at, update_at)
    VALUES 
        (1, 'INUOTATION', 0, NOW(), NOW()), 
        (2, 'INREVIEWFORWORKER', 0, NOW(), NOW()), 
        (3, 'INCOMPLETE', 0, NOW(), NOW()),
        (4, 'APPROVED', 0, NOW(), NOW()),
        (5, 'INREVIEWFORCLIENT', 0, NOW(), NOW()),
        (6, 'PENDINGAPPROVAL', 0, NOW(), NOW()),
        (7, 'REJECTED_BY_DAMAGE', 0, NOW(), NOW()),
        (8, 'DEADLINE_EXPIRED', 0, NOW(), NOW());
END 


CREATE PROCEDURE insert_default_states_damage()
BEGIN
    INSERT IGNORE INTO damages_state_cases (id, name, is_deleted, created_at, update_at)
    VALUES 
        (1, 'MILD', 0, NOW(), NOW()), 
        (2, 'MEDIUM', 0, NOW(), NOW()), 
        (3, 'HIGH', 0, NOW(), NOW());
END 




CALL insert_default_states_cases()
CALL insert_default_states_damage()
