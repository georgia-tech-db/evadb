import pandas as pd


class Dataset():
    def __init__(self, args=None):
        self.id = args['id']
        self.name = args['name']
        self.num_frames = args['num_frames']
        self.num_videos = args['num_videos']
        self.loaded_height = args['loaded_height']
        self.loaded_width = args['loaded_width']
        self.orig_height = args['orig_height']
        self.orig_width = args['orig_width']
        self.start_video_id = args['start_video_id']
        self.end_video_id = args['end_video_id']

    def __str__(self):
        return 'Dataset(name=' + self.name + ', height=' + str(
            self.loaded_height) + ', width=' + str(self.loaded_width) + ', ' \
            'num_frames=' + str(self.num_frames) + ', num_videos=' + \
            str(self.num_videos) + ')'

    @staticmethod
    def get(conn, name):
        sql = """SELECT * FROM dataset WHERE name = '%s'""" % (name)
        df = pd.read_sql_query(sql, conn)
        results = [Dataset(args) for args in df.to_dict(orient='records')]
        if len(results) == 1:
            return results[0]
        elif len(results) == 0:
            raise Exception('Dataset does not exist.')

    @staticmethod
    def create(conn, name, orig_height, orig_width, loaded_height,
               loaded_width):
        sql = """INSERT INTO dataset(name, orig_height, orig_width, 
        loaded_height, loaded_width) VALUES ('%s', %s, %s, %s, 
        %s)""" % (name, orig_height, orig_width, loaded_height, loaded_width)
        conn.execute(sql)

    @staticmethod
    def increment(conn, name, num_frames, num_videos):
        sql = """UPDATE dataset SET num_videos = num_videos + %s, num_frames 
        = num_frames + %s WHERE 
        name = '%s'""" % (num_videos, num_frames, name)
        conn.execute(sql)

    @staticmethod
    def delete_all(conn, name):
        sql = """DELETE FROM dataset WHERE name = '%s'""" % name
        conn.execute(sql)
