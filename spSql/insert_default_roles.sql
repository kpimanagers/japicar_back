DROP PROCEDURE IF EXISTS insert_default_roles;



CREATE PROCEDURE insert_default_roles()
BEGIN
    INSERT IGNORE INTO roles (id, name, is_deleted, created_at, update_at)
    VALUES 
        (1, 'CLIENTS', 0, NOW(), NOW()), 
        (2, 'OPERATIONS', 0, NOW(), NOW()), 
        (3, 'WORKSHOPS', 0, NOW(), NOW());
END 




CALL insert_default_roles()
