from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from src.configuration.configuration_manager import ConfigurationManager


class SQLConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SQLConfig, cls).__new__(cls)

            cls._instance.setup()

        return cls._instance

    def setup(self):
        self.engine = create_engine(ConfigurationManager()
                                    .get_value("core",
                                               "sqlalchemy_database_uri"))
        self.db_session = scoped_session(
            sessionmaker(autocommit=True, bind=self.engine))
