DROP PROCEDURE IF EXISTS insert_default_status_quote_case;



CREATE PROCEDURE insert_default_status_quote_case()
BEGIN
    INSERT IGNORE INTO status_quote_cases (id, name, is_deleted, created_at, update_at)
    VALUES 
        (1, 'PENDING', 0, NOW(), NOW()), 
        (2, 'APPROVED', 0, NOW(), NOW()), 
        (3, 'REJECTED', 0, NOW(), NOW()),
        (4, 'NOT_SEND', 0, NOW(), NOW());
END 




CALL insert_default_status_quote_case()
