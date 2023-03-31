--- create database audio;

USE audio;
CREATE TABLE audio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    artist VARCHAR(100) NOT NULL,
    album VARCHAR(100) NOT NULL,
    genre VARCHAR(100) NOT NULL,
    length INT NOT NULL
);

CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE playlist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE audio_playlist (
  audio_id INTEGER,
  playlist_id INTEGER,
  PRIMARY KEY (audio_id, playlist_id),
  FOREIGN KEY (audio_id) REFERENCES audio(id),
  FOREIGN KEY (playlist_id) REFERENCES playlist(id)
);
