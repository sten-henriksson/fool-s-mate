-- Create a general logs table for other logging needs
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    level TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT
);
