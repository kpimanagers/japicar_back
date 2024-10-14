DROP PROCEDURE IF EXISTS insert_default_workshops;
DROP PROCEDURE IF EXISTS insert_default_workshops_types;


CREATE PROCEDURE insert_default_workshops_types()
BEGIN
    INSERT IGNORE INTO workshop_types (id, name, created_at, update_at)
    VALUES 
        (1, 'A+', NOW(), NOW()),
        (2, 'A', NOW(), NOW()),
        (3, 'B', NOW(), NOW()),
        (4, 'C', NOW(), NOW());
END



CREATE PROCEDURE insert_default_workshops()
BEGIN
    INSERT IGNORE INTO workshops (id, name, region_id, commune_id, phone, email, is_deleted, created_at, update_at, type_id, rut, name_short)
    VALUES 
        (1, 'Mediterraneo Automotrores', 16, 269, '999199614', 'ricardo@circuloautos.cl', 0, NOW(), NOW(), 3, '96.889.440-4', 'Circulo'),
        (2, 'DyP Anfruns motors SPA', 16, 286, '959000948', 'mfuentes@anfrunsmotor.cl', 0, NOW(), NOW(), 2, '76.948.555-4', 'Anfruns'),
        (3, 'Servicios Automotrices Sergio Jabalquinto SpA', 16, 280, '967307577', 'sjabalquinto@gmail.com', 0, NOW(), NOW(), 3, '76.546.851-5', 'Jabalquinto'),
        (4, 'Taller de prueba', 16, 280, '123123123', 'taller@taller.cl', 0, NOW(), NOW(), 3, '56.456.789-3', 'tall');
        
        
END 




CALL insert_default_workshops()
CALL insert_default_workshops_types()
