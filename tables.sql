CREATE DATABASE test_db;
USE test_db;

CREATE TABLE Users (
--  column:        type:             constraints:
    id             UNIQUEIDENTIFIER  PRIMARY KEY,
    [login]        VARCHAR(20)       UNIQUE NOT NULL,
    [password]     VARCHAR(20)       NOT NULL
);

CREATE TABLE Administrators (
--  column:        type:             constraints:
    id             UNIQUEIDENTIFIER  PRIMARY KEY,
    [login]        VARCHAR(20)       UNIQUE NOT NULL,
    [password]     VARCHAR(20)       NOT NULL
);

CREATE TABLE Tests (
--  column:        type:             constraints:
    id             UNIQUEIDENTIFIER  PRIMARY KEY,
    [name]         VARCHAR(255)      UNIQUE NOT NULL,
    [description]  VARCHAR(255)      NOT NULL
);

CREATE TABLE Questions (
--  column:        type:             constraints:
    id             UNIQUEIDENTIFIER  PRIMARY KEY,
    test_id        UNIQUEIDENTIFIER  FOREIGN KEY REFERENCES Tests(id),
    [text]         VARCHAR(255)      NOT NULL
);

CREATE TABLE Answers (
--  column:        type:             constraints:
    id             UNIQUEIDENTIFIER  PRIMARY KEY,
    question_id    UNIQUEIDENTIFIER  FOREIGN KEY REFERENCES Questions(id),
    [text]         VARCHAR(255)      NOT NULL,
    is_correct     BIT               NOT NULL
);

CREATE TABLE Results (
--  column:        type:             constraints:
    id             UNIQUEIDENTIFIER  PRIMARY KEY,
    [user_id]      UNIQUEIDENTIFIER  FOREIGN KEY REFERENCES Users(id),
    test_id        UNIQUEIDENTIFIER  FOREIGN KEY REFERENCES Tests(id),
    [date]         DATETIME          NOT NULL DEFAULT(GETDATE()),
    best_attempt   FLOAT             NOT NULL CHECK(best_attempt BETWEEN 0 AND 1),
    last_attempt   FLOAT             NOT NULL CHECK(last_attempt BETWEEN 0 AND 1)
);

CREATE TABLE AnswerLogs (
--  column:        type:             constraints:
    id             UNIQUEIDENTIFIER  PRIMARY KEY,
    [user_id]      UNIQUEIDENTIFIER  FOREIGN KEY REFERENCES Users(id),
    question_id    UNIQUEIDENTIFIER  FOREIGN KEY REFERENCES Questions(id),
    answer_id      UNIQUEIDENTIFIER  FOREIGN KEY REFERENCES Answers(id),
    [date]         DATETIME          NOT NULL DEFAULT(GETDATE()),
    correct_flag   BIT               NOT NULL
);