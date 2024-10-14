DROP PROCEDURE IF EXISTS insert_default_no_participation_motive;



CREATE PROCEDURE insert_default_no_participation_motive()
BEGIN
    INSERT IGNORE INTO no_participation_motives (id, name, description, is_deleted, created_at, update_at)
    VALUES 
        (1, 'LACK_OF_INFO', 'Falta de información', 0, NOW(), NOW()), 
        (2, 'NOT_TIME', 'No tengo cupo', 0, NOW(), NOW()), 
        (3, 'NOT_WORKER_FOR_CASE', 'No tengo profesional al caso', 0, NOW(), NOW()),
        (4, 'ALL', 'Todas las anteriores', 0, NOW(), NOW());
END 


CALL insert_default_no_participation_motive()
