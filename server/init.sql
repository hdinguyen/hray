-- Create the feedback table if it doesn't exist
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    thread_id VARCHAR,
    question TEXT,
    response TEXT,
    helpful BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ignore BOOLEAN NOT NULL DEFAULT FALSE
);

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE hray TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
