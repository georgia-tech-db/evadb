CREATE TABLE IF NOT EXISTS dataset(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    num_frames INTEGER DEFAULT 0,
    num_videos INTEGER DEFAULT 0,
    orig_height INTEGER NOT NULL,
    orig_width INTEGER NOT NULL,
    loaded_height INTEGER DEFAULT NULL,
    loaded_width INTEGER DEFAULT NULL
);

-- CREATE TABLE IF NOT EXISTS uadetrac_frames(
--     id INTEGER PRIMARY KEY,
-- 	video_id INTEGER NOT NULL
-- );