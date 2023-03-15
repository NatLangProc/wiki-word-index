DROP TABLE IF EXISTS `words_pages`;
CREATE TABLE `words_pages` (
  `idpos` tinyint unsigned NOT NULL,
  `hword` bigint unsigned NOT NULL,
  `idpages` int unsigned NOT NULL,
  `numpages` int unsigned DEFAULT NULL,
  `numwords` int unsigned DEFAULT NULL,
  PRIMARY KEY (`idpos`,`hword`,`idpages`),
  KEY `fk_words_pages_2_idx` (`idpages`),
  CONSTRAINT `fk_words_pages_1` FOREIGN KEY (`idpos`, `hword`) REFERENCES `words` (`idpos`, `hword`),
  CONSTRAINT `fk_words_pages_2` FOREIGN KEY (`idpages`) REFERENCES `pages` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
