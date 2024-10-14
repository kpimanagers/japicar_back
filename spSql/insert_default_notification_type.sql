DROP PROCEDURE IF EXISTS insert_default_notification_type;



CREATE PROCEDURE insert_default_notification_type()
BEGIN
    INSERT IGNORE INTO notification_types (id, name, is_deleted, created_at, update_at)
    VALUES 
        (1, 'SYSTEM_ALERT', 0, NOW(), NOW()), 
        (2, 'REMINDER', 0, NOW(), NOW()), 
        (3, 'STATUS_CHANGE', 0, NOW(), NOW()),
        (4, 'NOTIFY_OPERATOR_RELEASED_CASE_FOR_QUOTATION', 0, NOW(), NOW()),
        (5, 'NOTIFY_SHOP_SUBMITTED_QUOTE', 0, NOW(), NOW()),
        (6, 'NOTIFY_NEW_CASE_CREATED', 0, NOW(), NOW()),
        (7, 'NOTIFY_CHANGE_INFO_CASE', 0, NOW(), NOW()),
        (8, 'NOTIFY_QUOTATION_APPROVED', 0, NOW(), NOW()),
        (9, 'NOTIFY_ADDED_QUOTE_TO_CASE', 0, NOW(), NOW()),
        (10, 'NOTIFY_AWARDED_QUOTE_CASE_TO_OPERATIONS', 0, NOW(), NOW()),
        (11, 'NOTIFY_AWARDED_QUOTE_CASE_TO_WORKSHOP', 0, NOW(), NOW()),
        (12, 'NOTIFY_REJECTED_BY_DAMAGE', 0, NOW(), NOW()),
        (13, 'NOTIFY_DEADLINE_EXPIRED', 0, NOW(), NOW()),
        (14, 'NOTIFY_SHOP_SUBMITTED_QUOTE_RESPONSE', 0, NOW(), NOW()),
        (15, 'NOTIFY_WELCOME', 0, NOW(), NOW()),
        (16, 'NOTIFY_NEW_CASE_CREATED_CLIENT', 0, NOW(), NOW()),
        (17, 'NOTIFY_AWARDED_QUOTE_CASE_TO_CLIENT', 0, NOW(), NOW()),
        (18, 'NOTIFY_OPERATOR_RELEASED_CASE_FOR_QUOTATION_TO_CLIENT', 0, NOW(), NOW()),
        (19, 'NOTIFY_NEW_CLIENT', 0, NOW(), NOW());

END 




CALL insert_default_notification_type()
