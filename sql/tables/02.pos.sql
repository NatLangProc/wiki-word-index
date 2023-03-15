DROP TABLE IF EXISTS `pos`;
CREATE TABLE `pos` (
  `id` tinyint unsigned NOT NULL,
  `spacy` varchar(6) NOT NULL,
  `desc` varchar(32) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
