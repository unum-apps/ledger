CREATE TABLE IF NOT EXISTS `ledger`.`river` (
  `id` BIGINT AUTO_INCREMENT,
  `who` VARCHAR(255) NOT NULL,
  `what` JSON NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `who` (`who`)
);

CREATE TABLE IF NOT EXISTS `ledger`.`twain` (
  `id` BIGINT AUTO_INCREMENT,
  `river_id` BIGINT,
  `who` VARCHAR(255) NOT NULL,
  `what` JSON NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `river_id_who` (`river_id`,`who`)
);
