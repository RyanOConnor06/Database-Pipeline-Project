/*
 * Database Pipeline Project
 * Copyright (c) 2026 Ryan Patrick O'Connor. All rights reserved.
 *
 * Licensed for non-commercial use only, with required attribution.
 * See LICENSE.md for full terms.
 */

-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema roconnor7
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema roconnor7
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `roconnor7` DEFAULT CHARACTER SET utf8 ;
USE `roconnor7` ;

-- -----------------------------------------------------
-- Table `roconnor7`.`project_player`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `roconnor7`.`project_player` ;

CREATE TABLE IF NOT EXISTS `roconnor7`.`project_player` (
  `playerID` INT NOT NULL AUTO_INCREMENT,
  `firstName` VARCHAR(45) NULL,
  `lastName` VARCHAR(45) NULL,
  PRIMARY KEY (`playerID`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `roconnor7`.`project_season`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `roconnor7`.`project_season` ;

CREATE TABLE IF NOT EXISTS `roconnor7`.`project_season` (
  `seasonID` INT NOT NULL,
  `year` YEAR NULL,
  PRIMARY KEY (`seasonID`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `roconnor7`.`project_opponent`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `roconnor7`.`project_opponent` ;

CREATE TABLE IF NOT EXISTS `roconnor7`.`project_opponent` (
  `opponentID` INT NOT NULL AUTO_INCREMENT,
  `teamName` VARCHAR(60) NULL,
  PRIMARY KEY (`opponentID`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `roconnor7`.`project_game`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `roconnor7`.`project_game` ;

CREATE TABLE IF NOT EXISTS `roconnor7`.`project_game` (
  `gameID` INT NOT NULL AUTO_INCREMENT,
  `seasonID` INT NOT NULL,
  `result` CHAR(1) NULL,
  `date` DATE NULL,
  `opponentID` INT NOT NULL,
  PRIMARY KEY (`gameID`, `seasonID`),
  INDEX `fk_game_season_idx` (`seasonID` ASC) VISIBLE,
  INDEX `fk_project_game_project_opponent1_idx` (`opponentID` ASC) VISIBLE,
  CONSTRAINT `fk_game_season`
    FOREIGN KEY (`seasonID`)
    REFERENCES `roconnor7`.`project_season` (`seasonID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_project_game_project_opponent1`
    FOREIGN KEY (`opponentID`)
    REFERENCES `roconnor7`.`project_opponent` (`opponentID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `roconnor7`.`project_player_has_game`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `roconnor7`.`project_player_has_game` ;

CREATE TABLE IF NOT EXISTS `roconnor7`.`project_player_has_game` (
  `seasonID` INT NOT NULL,
  `gameID` INT NOT NULL,
  `playerID` INT NOT NULL,
  `plateAppearances` INT NULL,
  `atBats` INT NULL,
  `hits` INT NULL,
  `homeRuns` INT NULL,
  `walks` INT NULL,
  `strikeOuts` INT NULL,
  `totalBases` INT NULL,
  `winProbabilityAdded` DECIMAL(4,3) NULL,
  `stolenBases` INT NULL,
  PRIMARY KEY (`seasonID`, `gameID`, `playerID`),
  INDEX `fk_player_has_game_game1_idx` (`gameID` ASC, `seasonID` ASC) VISIBLE,
  INDEX `fk_player_has_game_player1_idx` (`playerID` ASC) VISIBLE,
  CONSTRAINT `fk_player_has_game_player1`
    FOREIGN KEY (`playerID`)
    REFERENCES `roconnor7`.`project_player` (`playerID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_player_has_game_game1`
    FOREIGN KEY (`gameID` , `seasonID`)
    REFERENCES `roconnor7`.`project_game` (`gameID` , `seasonID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `roconnor7`.`project_position`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `roconnor7`.`project_position` ;

CREATE TABLE IF NOT EXISTS `roconnor7`.`project_position` (
  `positionID` INT NOT NULL,
  `positionName` VARCHAR(20) NULL,
  PRIMARY KEY (`positionID`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `roconnor7`.`project_player_game_has_position`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `roconnor7`.`project_player_game_has_position` ;

CREATE TABLE IF NOT EXISTS `roconnor7`.`project_player_game_has_position` (
  `seasonID` INT NOT NULL,
  `gameID` INT NOT NULL,
  `playerID` INT NOT NULL,
  `positionID` INT NOT NULL,
  PRIMARY KEY (`seasonID`, `gameID`, `playerID`, `positionID`),
  INDEX `fk_project_player_has_game_has_project_position_project_pos_idx` (`positionID` ASC) VISIBLE,
  INDEX `fk_project_player_has_game_has_project_position_project_pla_idx` (`seasonID` ASC, `gameID` ASC, `playerID` ASC) VISIBLE,
  CONSTRAINT `fk_project_player_has_game_has_project_position_project_playe1`
    FOREIGN KEY (`seasonID` , `gameID` , `playerID`)
    REFERENCES `roconnor7`.`project_player_has_game` (`seasonID` , `gameID` , `playerID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_project_player_has_game_has_project_position_project_posit1`
    FOREIGN KEY (`positionID`)
    REFERENCES `roconnor7`.`project_position` (`positionID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
