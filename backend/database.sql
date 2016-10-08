CREATE TABLE Users
(
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	email TEXT
);	

CREATE TABLE Room
(
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	creator INT NOT NULL REFERENCES User(id) ,
	timeLimit TIMESTAMP,
	questionLimit INT,
	status ENUM('waiting', 'started', 'finished', 'closed')
);

CREATE TABLE Question
(
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	roomId INT REFERENCES Room(id),
	question TEXT
);

CREATE TABLE Answer
(
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	questionId INT REFERENCES Question(id),
	userId INT REFERENCES User(id),
	answer TEXT
);

CREATE TABLE QuizQuestion
(
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	userId INT REFERENCES User(id),
	roomId INT REFERENCES Room(id),
	answerId INT REFERENCES Answer(id)
);

CREATE TABLE QuizPossibleAnswer
(
	quizId INT,
	answerId INT,
	PRIMARY KEY(quizId, answerId)
);