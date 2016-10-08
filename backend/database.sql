CREATE TABLE Users
(
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	email TEXT
);	

CREATE TABLE Room
(
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	creator INT NOT NULL REFERENCES Users(id) ,
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
	userId INT REFERENCES Users(id),
	answer TEXT
);

CREATE TABLE QuizQuestion
(
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	askedUserId INT REFERENCES Users(id),
	aboutUserId INT REFERENCES Users(id),
	roomId INT REFERENCES Room(id),
	answerId INT REFERENCES Answer(id),
	answeredId INT REFERENCES Answer(id)
);

CREATE TABLE QuizPossibleAnswer
(
	quizId INT REFERENCES QuizQuestion(id),
	answerId INT REFERENCES Answer(id),
	PRIMARY KEY(quizId, answerId)
);