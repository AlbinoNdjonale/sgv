DROP TABLE IF EXISTS `produto`;

CREATE TABLE `produto` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(30) NOT NULL,
  `preco` int(11) NOT NULL,
  `estoque` int(11) NOT NULL,
  `prazo` date DEFAULT NULL,
  `fornecedor` varchar(50) DEFAULT NULL,
  `tipo` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_estonian_ci;

DROP TABLE IF EXISTS `produtovendido`;

CREATE TABLE `produtovendido` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `produto` int(11) NOT NULL,
  `venda` int(11) NOT NULL,
  `quantidade` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `produto` (`produto`,`venda`),
  KEY `venda` (`venda`),
  CONSTRAINT `produtovendido_ibfk_1` FOREIGN KEY (`produto`) REFERENCES `produto` (`id`),
  CONSTRAINT `produtovendido_ibfk_2` FOREIGN KEY (`venda`) REFERENCES `venda` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

DROP TABLE IF EXISTS `venda`;

CREATE TABLE `venda` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `data` date NOT NULL,
  `vendedor` int(11) NOT NULL,
  `cliente` varchar(50) NOT NULL,
  `totalpago` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `vendedor` (`vendedor`),
  CONSTRAINT `venda_ibfk_1` FOREIGN KEY (`vendedor`) REFERENCES `vendedor` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

DROP TABLE IF EXISTS `vendedor`;

CREATE TABLE `vendedor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(30) NOT NULL,
  `contacto` varchar(50) NOT NULL,
  `data` date NOT NULL,
  `senha` varchar(50) NOT NULL,
  `admin` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

DROP TABLE IF EXISTS `log`;

CREATE TABLE `log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(20) NOT NULL,
  `date` date NOT NULL,
  `content` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

DROP TABLE IF EXISTS `log`;

CREATE TABLE `info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `key` varchar(20) NOT NULL,
  `value` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

INSERT INTO `info` (`key`, `value`) VALUES ('nome', 'nomedoestabelecimento');
INSERT INTO `info` (`key`, `value`) VALUES ('localizacao', 'localizacaodoestabelecimento');
INSERT INTO `info` (`key`, `value`) VALUES ('nif', 'nifdoestabelecimento');
INSERT INTO `info` (`key`, `value`) VALUES ('contacto', 'contactodoestabelecimento');
