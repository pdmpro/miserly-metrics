-- MySQL DDL to create the simple database metrics table

USE YOUR_MYSQL_DATABASE;

CREATE TABLE `MetricsSummary` (
  `eventId` int NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `pageId` varchar(256) DEFAULT NULL, -- IMPORTANT: 256 isn't big enough if this is a URL; change it as needed.
  `hostname` varchar(64) DEFAULT NULL,
  `clicks` mediumint(8) unsigned DEFAULT NULL,
  `mouseleaves` mediumint(8) unsigned DEFAULT NULL,
  `mousemoveHalts` mediumint(8) unsigned DEFAULT NULL,
  `mousemovePixels` mediumint(8) unsigned DEFAULT NULL,
  `resizeHalts` mediumint(8) unsigned DEFAULT NULL,
  `resizePixels` mediumint(8) unsigned DEFAULT NULL,
  `scrollHalts` mediumint(8) unsigned DEFAULT NULL,
  `scrollPixels` mediumint(8) unsigned DEFAULT NULL,
  PRIMARY KEY (`eventId`),
  KEY `created` (`created`),
  KEY `pageId` (`pageId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
