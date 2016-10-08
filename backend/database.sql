CREATE TABLE User
(
	id INT PRIMARY KEY,
	mail TEXT
);

CREATE TABLE Room
(
	id INT PRIMARY KEY,
	creator INT REFERENCES User(id),
	timeLimit TIMESTAMP
);

CREATE TABLE Question
(
	id INT PRIMARY KEY,
	roomId INT REFERENCES Room(id)
	question TEXT
);

CREATE TABLE Answer
(
	id INT PRIMARY KEY,
	questionId INT REFERENCES Question(id),
	userId INT REFERENCES User(id),
	answer TEXT
);

CREATE TABLE QuizQuestion
(
	id INT PRIMARY KEY,
	userId INT REFERENCES User(id),
	roomId INT REFERENCES Room(id),
	answerId INT REFERENCES Answer(id)
);

CREATE TABLE QuizPossibleAnswer
(
	quizId INT,
	answerId INT
	PRIMARY KEY(quizId, answerId)
);