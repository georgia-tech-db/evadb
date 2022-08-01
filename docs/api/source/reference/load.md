# UPLOAD and LOAD keyword

## Syntax

## Example Queries

Before loading any video and structure data (e.g., csv files) into EVA, we need to **UPLOAD** the file to the EVA server.

### 1. Upload the data file to the EVA server

```mysql
 UPLOAD INFILE 'data/ua_detrac/ua_detrac.mp4' PATH 'test_video.mp4';
```

In this case:
- the video file is stored on the local path **data/ua_detrac/uda_detrac.mp4**.
- After the UPLOAD, the video file will be stored on the **[prefix]/test_video.mp4** on the server. 
- The **[prefix]** can be configured in **~/eva/eva.yml** on the server. 

### 2. Load the video file

```mysql
LOAD DATA INFILE 'test_video.mp4' INTO MyVideo WITH FORMAT VIDEO;
```
- **test_video.mp4** is the path (there is no need to specify the [prefix]) on the server when UPLOAD the video file.
- **MyVideo** is the table name for this video, and we will use this table name to refer the video in the subsequent queries.
- **WITH FORMAT VIDEO** is optional. By default, EVA considers it as a video **LOAD** query. 

When **LOAD** a video file, we don't need to create a schema for the table. Instead, EVA will automitically generate that.
The below is the schame that EVA uses for video tables.
|id|data|
|-|-|
|1|numpy.ndarray([...])|
|2|numpy.ndarray([...])|
Every row is a tuple of frame id and frame content (in numpy).

### 3. Load the csv file

To **LOAD** a csv file, we need to first create a schema so EVA knows the columns and types. 

```mysql
CREATE TABLE IF NOT EXISTS MyCSV (
                id INTEGER UNIQUE,
                frame_id INTEGER,
                video_id INTEGER,
                dataset_name TEXT(30),
                label TEXT(30),
                bbox NDARRAY FLOAT32(4),
                object_id INTEGER
            );
LOAD DATA INFILE 'test_metadata.csv' INTO MyCSV WITH FORMAT CSV;
```

- **test_metadata.csv** needs to be uploaded to the server using **UPLOAD**, similar to the **test_video.mp4**.
- The csv file can contain more columns than needed, EVA will only load the columns in the defined schema.
- **WITH FORMAT CSV** is required.




