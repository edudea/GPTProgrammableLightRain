DROP TABLE IF EXISTS chats;

CREATE TABLE chats (
                       id TEXT PRIMARY KEY,
                       createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                       updatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                       name TEXT NOT NULL,
                       deleted BOOLEAN NOT NULL DEFAULT FALSE
);

DROP TABLE IF EXISTS conversations;

CREATE TABLE conversations (
                               id TEXT PRIMARY KEY,
                               chatId INTEGER NOT NULL,
                               createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                               updatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                               description TEXT NOT NULL,
                               answer TEXT NOT NULL,
                               code TEXT DEFAULT UNKNOWN,
                               deleted BOOLEAN NOT NULL DEFAULT FALSE,
                               FOREIGN KEY (chatId) REFERENCES chats(id)
);
