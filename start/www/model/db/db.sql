CREATE TABLE `blogs`
(
    `id`         varchar(50)  NOT NULL,
    `user_id`    varchar(50)  NOT NULL,
    `user_name`  varchar(50)  NOT NULL,
    `user_image` varchar(500) NOT NULL,
    `name`       varchar(50)  NOT NULL,
    `summary`    varchar(200) NOT NULL,
    `content`    mediumtext   NOT NULL,
    `created_at` double       NOT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_created_at` (`created_at`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8;

CREATE TABLE `comments`
(
    `id`         varchar(50)  NOT NULL,
    `blog_id`    varchar(50)  NOT NULL,
    `user_id`    varchar(50)  NOT NULL,
    `user_name`  varchar(50)  NOT NULL,
    `user_image` varchar(500) NOT NULL,
    `content`    mediumtext   NOT NULL,
    `created_at` double       NOT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_created_at` (`created_at`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8;

CREATE TABLE `users`
(
    `id`         varchar(50)  NOT NULL,
    `email`      varchar(50)  NOT NULL,
    `passwd`     varchar(50)  NOT NULL,
    `admin`      tinyint(1)   NOT NULL,
    `name`       varchar(50)  NOT NULL,
    `image`      varchar(500) NOT NULL,
    `created_at` double       NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_email` (`email`),
    KEY `idx_created_at` (`created_at`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8;