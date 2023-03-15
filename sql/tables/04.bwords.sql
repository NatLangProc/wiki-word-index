DROP TABLE IF EXISTS `bwords`;
CREATE TABLE `bwords` (
  `hword` bigint unsigned NOT NULL,
  `idpos` tinyint unsigned NOT NULL,
  `word` varchar(128) NOT NULL,
  `count` int unsigned NOT NULL,
  `len` int unsigned NOT NULL,
  PRIMARY KEY (`hword`,`idpos`),
  KEY `fk_bwords_1_idx` (`idpos`),
  CONSTRAINT `fk_bwords_1` FOREIGN KEY (`idpos`) REFERENCES `pos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
