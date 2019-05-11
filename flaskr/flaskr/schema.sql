DROP TABLE IF EXISTS reply;
DROP TABLE IF EXISTS collects;
DROP TABLE IF EXISTS likes;
DROP TABLE IF EXISTS post_file;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS user;


CREATE TABLE user (
  id INT AUTO_INCREMENT PRIMARY KEY,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  username VARCHAR(40) UNIQUE NOT NULL,
  nickname VARCHAR(40) NOT NULL,
  password VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  is_block TINYINT(1) NOT NULL DEFAULT 0
);

CREATE TABLE post (
  id INT AUTO_INCREMENT PRIMARY KEY,
  author_id INT NOT NULL,
  num_view INT NOT NULL DEFAULT 0,
  num_reply INT NOT NULL DEFAULT 0,
  num_like INT NOT NULL DEFAULT 0,
  num_collect INT NOT NULL DEFAULT 0,
  hot DOUBLE NOT NULL DEFAULT 0,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  is_top TINYINT(1) NOT NULL DEFAULT 0,
  is_fine TINYINT(1) NOT NULL DEFAULT 0,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE post_file (
  id INT AUTO_INCREMENT PRIMARY KEY,
  post_id INT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  filename TEXT NOT NULL,
  filehash TEXT NOT NULL,
  FOREIGN KEY (post_id) REFERENCES post (id)
);

CREATE TABLE reply (
  id INT AUTO_INCREMENT PRIMARY KEY,
  author_id INT NOT NULL,
  post_id INT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id),
  FOREIGN KEY (post_id) REFERENCES post (id)
);

CREATE TABLE collects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  author_id INT NOT NULL,
  post_id INT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id),
  FOREIGN KEY (post_id) REFERENCES post (id)
);

CREATE TABLE likes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  author_id INT NOT NULL,
  post_id INT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id),
  FOREIGN KEY (post_id) REFERENCES post (id)
);
CREATE UNIQUE INDEX USERNAME_INDEX ON user (username);
CREATE UNIQUE INDEX LIKES_INDEX ON likes (author_id, post_id);
CREATE UNIQUE INDEX COLLECTS_INDEX ON collects (author_id, post_id);


DROP TRIGGER IF EXISTS add_num_likes;
DROP TRIGGER IF EXISTS minus_num_likes;
DROP TRIGGER IF EXISTS add_num_collects;
DROP TRIGGER IF EXISTS minus_num_collects;
DROP TRIGGER IF EXISTS add_num_reply;
DROP TRIGGER IF EXISTS minus_num_reply;

CREATE TRIGGER add_num_likes
AFTER INSERT ON likes
FOR EACH ROW
UPDATE post SET num_like=num_like+1 WHERE id=NEW.post_id;

CREATE TRIGGER  minus_num_likes
BEFORE DELETE ON likes
FOR EACH ROW
UPDATE post SET num_like=num_like-1 WHERE id=OLD.post_id;

CREATE TRIGGER add_num_collects
AFTER INSERT ON collects
FOR EACH ROW
UPDATE post SET num_collect=num_collect+1 WHERE id=NEW.post_id;

CREATE TRIGGER  minus_num_collects
BEFORE DELETE ON collects
FOR EACH ROW
UPDATE post SET num_collect=num_collect-1 WHERE id=OLD.post_id;

CREATE TRIGGER add_num_reply
AFTER INSERT ON reply
FOR EACH ROW
UPDATE post SET num_reply=num_reply+1 WHERE id=NEW.post_id;

CREATE TRIGGER  minus_num_reply
BEFORE DELETE ON reply
FOR EACH ROW
UPDATE post SET num_reply=num_reply-1 WHERE id=OLD.post_id;


DROP PROCEDURE IF EXISTS delete_post;
DELIMITER  //
CREATE PROCEDURE delete_post(IN p_id INT)
BEGIN
SELECT filename, id FROM post_file WHERE post_id=p_id;
DELETE FROM collects WHERE post_id=p_id;
DELETE FROM likes WHERE post_id=p_id;
DELETE FROM reply WHERE post_id=p_id;
DELETE FROM post_file WHERE post_id=p_id;
DELETE FROM post WHERE id=p_id;
END
//
DELIMITER  ;
