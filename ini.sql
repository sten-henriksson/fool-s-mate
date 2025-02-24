-- SQL schema for agent code logging
CREATE TABLE IF NOT EXISTS code_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'code'
);

-- Index for faster timestamp-based queries
CREATE INDEX IF NOT EXISTS idx_code_logs_timestamp ON code_logs(timestamp);

-- View for formatted code logs
CREATE VIEW IF NOT EXISTS formatted_code_logs AS
SELECT 
    strftime('%Y-%m-%d %H:%M:%S', timestamp) AS formatted_time,
    title,
    content
FROM code_logs
ORDER BY timestamp DESC;
