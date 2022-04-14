from eva.configuration.configuration_manager import ConfigurationManager
from eva.utils.generic_utils import str_to_class

StorageEngine = str_to_class(
    ConfigurationManager().get_value(
        "storage", "engine"))()
VideoStorageEngine = str_to_class(
    ConfigurationManager().get_value(
        "storage", "video_engine"))()
