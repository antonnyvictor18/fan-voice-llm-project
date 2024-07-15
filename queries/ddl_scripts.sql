CREATE SCHEMA IF NOT EXISTS Brasileirao2023;

CREATE TABLE Brasileirao2023.Teams (
    team_id SERIAL PRIMARY KEY,
    team_name VARCHAR(255) NOT NULL
);

CREATE TABLE Brasileirao2023.Posts (
    post_id SERIAL PRIMARY KEY,
    team_id INT REFERENCES Brasileirao2023.Teams(team_id),
    post_date DATE NOT NULL,
    post_title TEXT NOT NULL,
    post_round INT NOT NULL,	
    reddit_post_id VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE Brasileirao2023.Comments (
    comment_id SERIAL PRIMARY KEY,
    post_id INT REFERENCES Brasileirao2023.Posts(post_id),
    comment_date TIMESTAMP NOT NULL,
    comment_content TEXT NOT NULL,
    comment_score INT NOT NULL,
    comment_sentiment VARCHAR(15) NOT NULL,
    reddit_comment_id VARCHAR(255) UNIQUE NOT NULL
);
