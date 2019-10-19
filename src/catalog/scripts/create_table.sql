CREATE TABLE IF NOT EXISTS dataset(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    num_frames INTEGER DEFAULT 0,
    num_videos INTEGER DEFAULT 0,
    orig_height INTEGER NOT NULL,
    orig_width INTEGER NOT NULL,
    loaded_height INTEGER DEFAULT NULL,
    loaded_width INTEGER DEFAULT NULL,
    start_video_id INTEGER DEFAULT NULL,
    end_video_id INTEGER DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS video_frame_map(
	video_id INTEGER PRIMARY KEY,
	start_frame_id TEXT NOT NULL,
	end_frame_id INTEGER NOT NULL
);