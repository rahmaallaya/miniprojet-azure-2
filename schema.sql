-- Base de donnees du mini projet (a executer sur vm-db avec: sudo mysql < schema.sql)
CREATE DATABASE IF NOT EXISTS miniprojet CHARACTER SET utf8mb4;

-- Utilisateur dedie, limite au sous-reseau de vm-app, droits minimaux
-- Remplacer CHANGE_ME par le vrai mot de passe
CREATE USER IF NOT EXISTS 'appuser'@'10.2.1.%' IDENTIFIED BY 'CHANGE_ME';
GRANT SELECT, INSERT, UPDATE, DELETE ON miniprojet.* TO 'appuser'@'10.2.1.%';
FLUSH PRIVILEGES;

USE miniprojet;

CREATE TABLE IF NOT EXISTS instruments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nom VARCHAR(100) NOT NULL,
  description VARCHAR(255),
  prix DECIMAL(10,2) NOT NULL,
  categorie VARCHAR(50)
);

INSERT INTO instruments (nom, description, prix, categorie) VALUES
('Guitare acoustique','Guitare en bois pour débutants et professionnels.',350.00,'Cordes'),
('Cajón','Instrument de percussion d''origine péruvienne.',150.00,'Percussions'),
('Trompette','Instrument de la famille des cuivres.',450.00,'Cuivres'),
('Saxophone','Instrument à vent de la famille des bois.',900.00,'Bois'),
('Violon','Instrument classique à cordes frottées.',500.00,'Cordes'),
('Batterie','Batterie complète pour musiciens avancés.',1200.00,'Percussions');
