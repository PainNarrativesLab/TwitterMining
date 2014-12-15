# ************************************************************
# Sequel Pro SQL dump
# Version 4096
#
# http://www.sequelpro.com/
# http://code.google.com/p/sequel-pro/
#
# Host: localhost (MySQL 5.6.21)
# Database: twitter_data
# Generation Time: 2014-11-13 21:02:15 +0000
# ************************************************************


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


# Dump of table hashtags
# ------------------------------------------------------------

CREATE TABLE `hashtags` (
  `tagID` bigint(30) unsigned NOT NULL AUTO_INCREMENT,
  `hashtag` text NOT NULL,
  PRIMARY KEY (`tagID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



# Dump of table tweets
# ------------------------------------------------------------

CREATE TABLE `tweets` (
  `tweetID` bigint(30) unsigned NOT NULL,
  `userID` bigint(30) unsigned NOT NULL,
  `tweetText` blob NOT NULL,
  `favorite_count` int(10) DEFAULT NULL,
  `source` text CHARACTER SET utf8,
  `retweeted` varchar(10) CHARACTER SET utf8 DEFAULT NULL,
  `in_reply_to_screen_name` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `retweet_count` int(10) DEFAULT NULL,
  `favorited` varchar(10) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `lang` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `created_at` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `profile_background_tile` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`tweetID`),
  KEY `userID` (`userID`),
  CONSTRAINT `tweets_ibfk_1` FOREIGN KEY (`userID`) REFERENCES `users` (`userID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



# Dump of table tweetsXtags
# ------------------------------------------------------------

CREATE TABLE `tweetsXtags` (
  `tweetID` bigint(30) unsigned NOT NULL,
  `tagID` bigint(30) unsigned NOT NULL,
  PRIMARY KEY (`tweetID`,`tagID`),
  KEY `tagID` (`tagID`),
  CONSTRAINT `tweetsxtags_ibfk_2` FOREIGN KEY (`tweetID`) REFERENCES `tweets` (`tweetID`),
  CONSTRAINT `tweetsxtags_ibfk_3` FOREIGN KEY (`tagID`) REFERENCES `hashtags` (`tagID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table users
# ------------------------------------------------------------

CREATE TABLE `users` (
  `userID` bigint(30) unsigned NOT NULL,
  `lang` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `utc_offset` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `verified` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `description` text CHARACTER SET utf8,
  `friends_count` int(10) DEFAULT NULL,
  `url` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `time_zone` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `created_at` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `name` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `entities` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `followers_count` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `screen_name` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `id_str` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `favourites_count` int(10) DEFAULT NULL,
  `statuses_count` int(10) DEFAULT NULL,
  `id` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `location` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  PRIMARY KEY (`userID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;




/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
