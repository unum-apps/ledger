CREATE TABLE IF NOT EXISTS `ledger`.`act` (
  `id` BIGINT AUTO_INCREMENT,
  `entity_id` BIGINT,
  `app_id` BIGINT,
  `when` BIGINT,
  `what` JSON NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `when` (`when`)
);

CREATE TABLE IF NOT EXISTS `ledger`.`app` (
  `id` BIGINT AUTO_INCREMENT,
  `who` VARCHAR(255) NOT NULL,
  `status` VARCHAR(255) NOT NULL DEFAULT 'active',
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `who` (`who`)
);

CREATE TABLE IF NOT EXISTS `ledger`.`award` (
  `id` BIGINT AUTO_INCREMENT,
  `entity_id` BIGINT,
  `who` VARCHAR(255) NOT NULL,
  `status` VARCHAR(255) NOT NULL DEFAULT 'requested',
  `when` BIGINT,
  `what` JSON NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `when` (`when`),
  UNIQUE `entity_id_who` (`entity_id`,`who`)
);

CREATE TABLE IF NOT EXISTS `ledger`.`entity` (
  `id` BIGINT AUTO_INCREMENT,
  `unum_id` BIGINT,
  `who` VARCHAR(255) NOT NULL,
  `status` VARCHAR(255) NOT NULL DEFAULT 'active',
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `unum_id_who` (`unum_id`,`who`)
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
  INDEX `when` (`when`)
);

CREATE TABLE IF NOT EXISTS `ledger`.`herald` (
  `id` BIGINT AUTO_INCREMENT,
  `entity_id` BIGINT,
  `app_id` BIGINT,
  `status` VARCHAR(255) NOT NULL DEFAULT 'active',
  `what` JSON NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `entity_id_app_id` (`entity_id`,`app_id`)
);

CREATE TABLE IF NOT EXISTS `ledger`.`journal` (
  `id` BIGINT AUTO_INCREMENT,
  `who` VARCHAR(255) NOT NULL,
  `what` JSON NOT NULL,
  `when` BIGINT,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `historical` (`when`),
  INDEX `personal` (`who`)
);

CREATE TABLE IF NOT EXISTS `ledger`.`origin` (
  `id` BIGINT AUTO_INCREMENT,
  `who` VARCHAR(255) NOT NULL,
  `status` VARCHAR(255) NOT NULL DEFAULT 'active',
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `who` (`who`)
);

CREATE TABLE IF NOT EXISTS `ledger`.`scat` (
  `id` BIGINT AUTO_INCREMENT,
  `entity_id` BIGINT,
  `who` VARCHAR(255) NOT NULL,
  `status` VARCHAR(255) NOT NULL DEFAULT 'recorded',
  `when` BIGINT,
  `what` JSON NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `when` (`when`)
);

CREATE TABLE IF NOT EXISTS `ledger`.`task` (
  `id` BIGINT AUTO_INCREMENT,
  `entity_id` BIGINT,
  `who` VARCHAR(255) NOT NULL,
  `status` VARCHAR(255) NOT NULL DEFAULT 'blocked',
  `when` BIGINT,
  `what` JSON NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `when` (`when`)
);

CREATE TABLE IF NOT EXISTS `ledger`.`unum` (
  `id` BIGINT AUTO_INCREMENT,
  `who` VARCHAR(255) NOT NULL,
  `status` VARCHAR(255) NOT NULL DEFAULT 'active',
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `who` (`who`)
);

CREATE TABLE IF NOT EXISTS `ledger`.`witness` (
  `id` BIGINT AUTO_INCREMENT,
  `entity_id` BIGINT,
  `origin_id` BIGINT,
  `who` VARCHAR(255) NOT NULL,
  `status` VARCHAR(255) NOT NULL DEFAULT 'active',
  `what` JSON NOT NULL,
  `meta` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `entity_id_origin_id_who` (`entity_id`,`origin_id`,`who`)
);
