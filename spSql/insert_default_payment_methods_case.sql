DROP PROCEDURE IF EXISTS insert_default_payment_methods_case;



CREATE PROCEDURE insert_default_payment_methods_case()
BEGIN
    INSERT IGNORE INTO payment_methods_cases (id, name, is_deleted, created_at, update_at)
    VALUES 
        (1, '50% adelanto / 50% entrega', 0, NOW(), NOW()), 
        (2, 'Tarjeta Debito / Crédito', 0, NOW(), NOW()), 
        (3, 'Otra forma', 0, NOW(), NOW());
END 




CALL insert_default_payment_methods_case()
