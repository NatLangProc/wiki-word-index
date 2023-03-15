DROP TABLE IF EXISTS `bwords_pages`;
CREATE TABLE `bwords_pages` (
  `idpos` tinyint unsigned NOT NULL,
  `hword` bigint unsigned NOT NULL,
  `idpages` int unsigned NOT NULL,
  `numpages` int unsigned DEFAULT NULL,
  `numwords` int unsigned DEFAULT NULL,
  PRIMARY KEY (`idpos`,`hword`,`idpages`),
  KEY `fk_bwords_pages_2_idx` (`idpages`),
  CONSTRAINT `fk_bwords_pages_1` FOREIGN KEY (`idpos`, `hword`) REFERENCES `bwords` (`idpos`, `hword`),
  CONSTRAINT `fk_bwords_pages_2` FOREIGN KEY (`idpages`) REFERENCES `pages` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
