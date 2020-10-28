from src.configuration.configuration_manager import ConfigurationManager
from src.utils.generic_utils import str_to_class

StorageEngine = str_to_class(
    ConfigurationManager().get_value(
        "storage", "engine"))()
