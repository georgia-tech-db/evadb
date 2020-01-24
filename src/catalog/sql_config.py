from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class SQLConfig(object):
    base = declarative_base()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SQLConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.engine = create_engine('mysql+pymysql://root:root@localhost/eva_catalog')
        self.session_factory = sessionmaker(bind=self.engine)
        self.session = self.session_factory()
        self.base.metadata.create_all(self.engine)

    def get_session(self):
        if self.session is None:
            self.session = self.session_factory()
        return self.session


sql_conn = SQLConfig()
