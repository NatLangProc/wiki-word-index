DROP TABLE IF EXISTS `blocks`;
CREATE TABLE `blocks` (
  `number` int unsigned NOT NULL,
  `start` bigint unsigned NOT NULL,
  `end` bigint unsigned NOT NULL,
  `processed` tinyint unsigned NOT NULL DEFAULT '0',
  `proctime` double DEFAULT NULL,
  `sqltime` double NOT NULL DEFAULT '0',
  `words` int unsigned DEFAULT NULL,
  `sum` bigint unsigned DEFAULT NULL,
  `newwords` int unsigned DEFAULT NULL,
  `maxlen` smallint unsigned DEFAULT NULL,
  PRIMARY KEY (`number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
