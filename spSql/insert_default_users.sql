DROP PROCEDURE IF EXISTS insert_default_users;



CREATE PROCEDURE insert_default_users()
BEGIN
    DECLARE user_password VARCHAR(255);
    SET user_password = '$2b$12$WDdm6UB8uj16MElRjKlAWuCbhGd.e8qBwW53WSWwktV9Y4g4T4XKq'; --123
    -- las contraseñas son: 1231, 1232, 1233 para los talleres

    INSERT IGNORE INTO users (id, email, phone, password, role_id, is_deleted, created_at, update_at, name, last_name, workshop_id)
    VALUES 
        (1, 'usuario@cliente.cl', '12312312', user_password, 1,  0, NOW(), NOW(), 'usuario', 'cliente', NULL),
        (2, 'usuario@operador.cl', '12312312', user_password, 2,  0, NOW(), NOW(), 'usuario', 'operador', NULL),
        (3, 'usuario@taller.cl', '12312312', user_password, 3,  0, NOW(), NOW(), 'usuario', 'taller', 4),
        (4, 'ricardo@circuloautos.cl', '99199614', '$2b$12$SXYGmj.MKujEQFw82OrfI.yigIakIQOyDOKIxK8Hulhh1scCZSXZS', 3,  0, NOW(), NOW(), 'Ricardo', 'Schnettle', 1),
        (5, 'mfuentes@anfrunsmotor.cl', '959000948', '$2b$12$m4x0D6.6EaOzWZMof8/CqOTFytrATpzqNw/n5wzbxezkL7CeeWcYi', 3,  0, NOW(), NOW(), 'Mauricio', 'Fuentes', 2),
        (6, 'sjabalquinto@gmail.com', '967307577', '$2b$12$bnCxPu5vDRyxX9j5CcdMvujR0x8oDob5vPb8NVs1Yjo4/X0OD2V0C', 3,  0, NOW(), NOW(), 'Mauricio', 'Fuentes', 3),
        (7, 'gerencia@jabalquinto.cl', '967307577', '$2b$12$bnCxPu5vDRyxX9j5CcdMvujR0x8oDob5vPb8NVs1Yjo4/X0OD2V0C', 3,  0, NOW(), NOW(), 'Jorge', 'Jabalquinto', 3);
        
        
END 




CALL insert_default_users()
