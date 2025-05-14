ALTER TABLE `ledger`.`app`
  ADD `status` VARCHAR(255) NOT NULL DEFAULT 'active';

ALTER TABLE `ledger`.`entity`
  ADD `status` VARCHAR(255) NOT NULL DEFAULT 'active';

ALTER TABLE `ledger`.`herald`
  ADD `status` VARCHAR(255) NOT NULL DEFAULT 'active';

ALTER TABLE `ledger`.`origin`
  ADD `status` VARCHAR(255) NOT NULL DEFAULT 'active';

ALTER TABLE `ledger`.`unum`
  ADD `status` VARCHAR(255) NOT NULL DEFAULT 'active';

ALTER TABLE `ledger`.`witness`
  ADD `status` VARCHAR(255) NOT NULL DEFAULT 'active';
