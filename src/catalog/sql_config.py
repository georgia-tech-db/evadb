from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from src.configuration.configuration_manager import ConfigurationManager


class SQLConfig:
    """Singleton class for configuring connection to the database.

    Attributes:
        _instance: stores the singleton instance of the class.
    """

    _instance = None

    def __new__(cls):
        """Overrides the default __new__ method.

        Returns the existing instance or creates a new one if an instance
        does not exist.

        Returns:
            An instance of the class.
        """
        if cls._instance is None:
            cls._instance = super(SQLConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initializes the engine and session for database operations

        Retrieves the database uri for connection from ConfigurationManager.
        """
        uri = ConfigurationManager().get_value("core",
                                               "sqlalchemy_database_uri")
        self.engine = create_engine(uri)  # set echo=True to log SQL statements
        self.session = scoped_session(sessionmaker(bind=self.engine))
