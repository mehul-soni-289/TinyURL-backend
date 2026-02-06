-- TinyURL Database Schema for Supabase (PostgreSQL)
-- Run this in Supabase SQL Editor

-- Create URLs table
CREATE TABLE IF NOT EXISTS urls (
    id BIGSERIAL PRIMARY KEY,
    original_url TEXT NOT NULL,
    short_code VARCHAR(10) UNIQUE,
    clicks INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    collision_resolved BOOLEAN DEFAULT FALSE,
    resolution_strategy VARCHAR(20)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_short_code ON urls(short_code);
CREATE INDEX IF NOT EXISTS idx_clicks ON urls(clicks DESC);
CREATE INDEX IF NOT EXISTS idx_created_at ON urls(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_original_url ON urls(original_url);

-- Add comments for documentation
COMMENT ON TABLE urls IS 'Stores shortened URLs with analytics';
COMMENT ON COLUMN urls.id IS 'Auto-increment ID used for Base62 encoding';
COMMENT ON COLUMN urls.original_url IS 'Original long URL';
COMMENT ON COLUMN urls.short_code IS 'Base62 encoded short code (unique)';
COMMENT ON COLUMN urls.clicks IS 'Number of times the short URL was accessed';
COMMENT ON COLUMN urls.created_at IS 'Timestamp when URL was created';
COMMENT ON COLUMN urls.collision_resolved IS 'Whether collision detection was triggered';
COMMENT ON COLUMN urls.resolution_strategy IS 'Strategy used to resolve collision (linear, regenerate, append)';

-- Optional: Create a function to automatically update clicks
CREATE OR REPLACE FUNCTION increment_clicks(p_short_code VARCHAR)
RETURNS INTEGER AS $$
DECLARE
    new_count INTEGER;
BEGIN
    UPDATE urls 
    SET clicks = clicks + 1 
    WHERE short_code = p_short_code
    RETURNING clicks INTO new_count;
    
    RETURN new_count;
END;
$$ LANGUAGE plpgsql;

-- Optional: Create a view for analytics
CREATE OR REPLACE VIEW url_analytics AS
SELECT 
    short_code,
    original_url,
    clicks,
    created_at,
    collision_resolved,
    resolution_strategy,
    CASE 
        WHEN clicks > 100 THEN 'High Traffic'
        WHEN clicks > 10 THEN 'Medium Traffic'
        ELSE 'Low Traffic'
    END as traffic_level
FROM urls
ORDER BY clicks DESC;

-- Verify tables created
SELECT table_name, column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'urls'
ORDER BY ordinal_position;
