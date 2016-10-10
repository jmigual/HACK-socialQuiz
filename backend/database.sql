CREATE TABLE users
(
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	email TEXT,
  name TEXT
);	

CREATE TABLE room
(
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	creator INT NOT NULL REFERENCES users(id) ,
	time_limit TIMESTAMP,
	question_limit INT,
	status ENUM('waiting', 'started', 'finished', 'closed') DEFAULT 'waiting'
);

CREATE TABLE room_members
(

	room_id INT REFERENCES room(id),
	user_id INT REFERENCES users(id),
	PRIMARY KEY(room_id, user_id)
);

CREATE TABLE question
(
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	room_id INT REFERENCES room(id),
	question TEXT
);

CREATE TABLE answer
(
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	question_id INT REFERENCES question (id),
	user_id INT REFERENCES users (id),
	answer TEXT
);

CREATE TABLE quiz_question
(
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	asked_user_id INT REFERENCES users (id),
	about_user_id INT REFERENCES users (id),
	question_id INT REFERENCES room (id),
	correct_answer_id INT REFERENCES answer (id),
	answered_id INT REFERENCES answer (id)
);

CREATE TABLE quiz_possible_answer
(
	quiz_id INT REFERENCES quiz_question (id),
	answer_id INT REFERENCES answer (id),
	PRIMARY KEY(quiz_id, answer_id)
);