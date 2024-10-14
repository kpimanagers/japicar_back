DROP PROCEDURE IF EXISTS delete_all_data;

CREATE PROCEDURE delete_all_data()
BEGIN
  -- Desactiva las restricciones de claves foráneas
  SET FOREIGN_KEY_CHECKS = 0;

  -- Elimina los datos en el orden que prefieras
  DELETE FROM accepted_terms;
  DELETE FROM accepted_terms_quote_cases;
  DELETE FROM awarded_quote_cases;
  DELETE FROM cars_cases;
  DELETE FROM cases;
  DELETE FROM contacts_cases;
  DELETE FROM images_cases;
  DELETE FROM notifications;
  DELETE FROM quote_items_cases;
  DELETE FROM quote_shops_cases;
  DELETE FROM quotes_cases;
  DELETE FROM seen_by;
  DELETE FROM shops_without_participation_cases;
  -- Repite para todas las tablas

  -- Vuelve a activar las restricciones de claves foráneas
  SET FOREIGN_KEY_CHECKS = 1;
END

CAll delete_all_data()
