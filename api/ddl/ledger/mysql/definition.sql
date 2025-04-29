CREATE TABLE IF NOT EXISTS `ledger`.`act` (
  `id` BIGINT AUTO_INCREMENT,
  `entity_id` BIGINT,
  `app_id` BIGINT,
  `when` BIGINT,
  `what` JSON NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `when` (`when`),
  UNIQUE `entity_id_app_id` (`entity_id`,`app_id`)
);

CREATE TABLE IF NOT EXISTS `ledger`.`app` (
  `id` BIGINT AUTO_INCREMENT,
  `who` VARCHAR(255) NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `who` (`who`)
);

CREATE TABLE IF NOT EXISTS `ledger`.`entity` (
  `id` BIGINT AUTO_INCREMENT,
  `unum_id` BIGINT,
  `who` VARCHAR(255) NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `unum_id_who` (`unum_id`,`who`)
);

CREATE TABLE IF NOT EXISTS `ledger`.`executor` (
  `id` BIGINT AUTO_INCREMENT,
  `entity_id` BIGINT,
  `app_id` BIGINT,
  `what` JSON NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `entity_id_app_id` (`entity_id`,`app_id`)
);

CREATE TABLE IF NOT EXISTS `ledger`.`fact` (
  `id` BIGINT AUTO_INCREMENT,
  `entity_id` BIGINT,
  `origin_id` BIGINT,
  `who` VARCHAR(255) NOT NULL,
  `when` BIGINT,
  `what` JSON NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `when` (`when`),
  UNIQUE `entity_id_origin_id` (`entity_id`,`origin_id`)
);

CREATE TABLE IF NOT EXISTS `ledger`.`herald` (
  `id` BIGINT AUTO_INCREMENT,
  `entity_id` BIGINT,
  `origin_id` BIGINT,
  `who` VARCHAR(255) NOT NULL,
  `what` JSON NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `entity_id_origin_id_who` (`entity_id`,`origin_id`,`who`)
);

CREATE TABLE IF NOT EXISTS `ledger`.`narrator` (
  `id` BIGINT AUTO_INCREMENT,
  `entity_id` BIGINT,
  `app_id` BIGINT,
  `what` JSON NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `entity_id_app_id` (`entity_id`,`app_id`)
);

CREATE TABLE IF NOT EXISTS `ledger`.`origin` (
  `id` BIGINT AUTO_INCREMENT,
  `who` VARCHAR(255) NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `who` (`who`)
);

CREATE TABLE IF NOT EXISTS `ledger`.`unum` (
  `id` BIGINT AUTO_INCREMENT,
  `who` VARCHAR(255) NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `who` (`who`)
);

CREATE TABLE IF NOT EXISTS `ledger`.`witness` (
  `id` BIGINT AUTO_INCREMENT,
  `entity_id` BIGINT,
  `origin_id` BIGINT,
  `who` VARCHAR(255) NOT NULL,
  `what` JSON NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `entity_id_origin_id_who` (`entity_id`,`origin_id`,`who`)
);
