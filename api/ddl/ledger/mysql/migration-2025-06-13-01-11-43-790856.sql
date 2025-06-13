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
