CREATE TABLE IF NOT EXISTS `ledger_app_unum`.`entity` (
  `id` BIGINT AUTO_INCREMENT,
  `unum_id` BIGINT,
  `who` VARCHAR(255) NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `unum_id_who` (`unum_id`,`who`)
);

CREATE TABLE IF NOT EXISTS `ledger_app_unum`.`fact` (
  `id` BIGINT AUTO_INCREMENT,
  `witness_id` BIGINT,
  `who` VARCHAR(255) NOT NULL,
  `when` BIGINT,
  `what` JSON NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `when` (`when`),
  UNIQUE `witness_id_who` (`witness_id`,`who`)
);

CREATE TABLE IF NOT EXISTS `ledger_app_unum`.`origin` (
  `id` BIGINT AUTO_INCREMENT,
  `who` VARCHAR(255) NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `who` (`who`)
);

CREATE TABLE IF NOT EXISTS `ledger_app_unum`.`unum` (
  `id` BIGINT AUTO_INCREMENT,
  `who` VARCHAR(255) NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `who` (`who`)
);

CREATE TABLE IF NOT EXISTS `ledger_app_unum`.`witness` (
  `id` BIGINT AUTO_INCREMENT,
  `entity_id` BIGINT,
  `origin_id` BIGINT,
  `who` VARCHAR(255) NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `entity_id_origin_id_who` (`entity_id`,`origin_id`,`who`)
);
