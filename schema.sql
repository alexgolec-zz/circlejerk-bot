CREATE TABLE IF NOT EXISTS already_tweeted(
    url VARCHAR(2048),
    sha_one CHAR(40),
    PRIMARY KEY (sha_one));
