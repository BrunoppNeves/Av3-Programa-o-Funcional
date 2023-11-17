def create_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `agencia_de_viagens`.`passageiro` (
        `id` INT NOT NULL AUTO_INCREMENT,
        `nome` VARCHAR(45) NOT NULL,
        `cpf` VARCHAR(45) NOT NULL,
        `email` VARCHAR(255) NOT NULL,
        `senha` VARCHAR(255) NOT NULL,
        PRIMARY KEY (`id`),
        UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
        UNIQUE INDEX `cpf_UNIQUE` (`cpf` ASC) VISIBLE)
        ENGINE = InnoDB;
    """)

    # Create cia_aerea table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `agencia_de_viagens`.`cia_aerea` (
        `id` INT NOT NULL AUTO_INCREMENT,
        `nome` VARCHAR(45) NOT NULL,
        PRIMARY KEY (`id`),
        UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
        UNIQUE INDEX `nome_UNIQUE` (`nome` ASC) VISIBLE)
        ENGINE = InnoDB;
    """)

    # Create cidade table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `agencia_de_viagens`.`cidade` (
        `id` INT NOT NULL AUTO_INCREMENT,
        `nome` VARCHAR(45) NOT NULL,
        PRIMARY KEY (`id`),
        UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE)
        ENGINE = InnoDB;
    """)

    # Create aeroporto table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `agencia_de_viagens`.`aeroporto` (
        `id` INT NOT NULL AUTO_INCREMENT,
        `cidade_id` INT NOT NULL,
        `nome` VARCHAR(45) NOT NULL,
        PRIMARY KEY (`id`),
        UNIQUE INDEX `idaeroporto_UNIQUE` (`id` ASC) VISIBLE,
        INDEX `fk_aeroporto_cidade_idx` (`cidade_id` ASC) VISIBLE,
        CONSTRAINT `fk_aeroporto_cidade`
            FOREIGN KEY (`cidade_id`)
            REFERENCES `agencia_de_viagens`.`cidade` (`id`)
            ON DELETE NO ACTION
            ON UPDATE NO ACTION)
        ENGINE = InnoDB;
    """)

    # Create voo table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `agencia_de_viagens`.`voo` (
        `id` INT NOT NULL AUTO_INCREMENT,
        `origem` INT NOT NULL,
        `destino` INT NOT NULL,
        `cia_aerea_id` INT NOT NULL,
        `horario` DATETIME NOT NULL,
        `valor` FLOAT NOT NULL,
        `vagas` INT NOT NULL,
        PRIMARY KEY (`id`),
        UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
        INDEX `fk_voo_aeroporto1_idx` (`origem` ASC) VISIBLE,
        INDEX `fk_voo_aeroporto2_idx` (`destino` ASC) VISIBLE,
        INDEX `fk_voo_cia_aerea1_idx` (`cia_aerea_id` ASC) VISIBLE,
        CONSTRAINT `fk_voo_aeroporto1`
            FOREIGN KEY (`origem`)
            REFERENCES `agencia_de_viagens`.`aeroporto` (`id`)
            ON DELETE NO ACTION
            ON UPDATE NO ACTION,
        CONSTRAINT `fk_voo_aeroporto2`
            FOREIGN KEY (`destino`)
            REFERENCES `agencia_de_viagens`.`aeroporto` (`id`)
            ON DELETE NO ACTION
            ON UPDATE NO ACTION,
        CONSTRAINT `fk_voo_cia_aerea1`
            FOREIGN KEY (`cia_aerea_id`)
            REFERENCES `agencia_de_viagens`.`cia_aerea` (`id`)
            ON DELETE NO ACTION
            ON UPDATE NO ACTION)
        ENGINE = InnoDB;
    """)

    # Create voo_has_passageiro table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `agencia_de_viagens`.`voo_has_passageiro` (
        `voo_id` INT NOT NULL,
        `passageiro_id` INT NOT NULL,
        PRIMARY KEY (`voo_id`, `passageiro_id`),
        INDEX `fk_voo_has_passageiro_passageiro1_idx` (`passageiro_id` ASC) VISIBLE,
        INDEX `fk_voo_has_passageiro_voo1_idx` (`voo_id` ASC) VISIBLE,
        CONSTRAINT `fk_voo_has_passageiro_voo1`
            FOREIGN KEY (`voo_id`)
            REFERENCES `agencia_de_viagens`.`voo` (`id`)
            ON DELETE NO ACTION
            ON UPDATE NO ACTION,
        CONSTRAINT `fk_voo_has_passageiro_passageiro1`
            FOREIGN KEY (`passageiro_id`)
            REFERENCES `agencia_de_viagens`.`passageiro` (`id`)
            ON DELETE NO ACTION
            ON UPDATE NO ACTION)
        ENGINE = InnoDB;
    """)
