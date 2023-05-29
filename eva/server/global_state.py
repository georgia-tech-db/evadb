import asyncio
import subprocess
from eva.configuration.configuration_manager import ConfigurationManager
from eva.interfaces.relational.db import EVAConnection
from eva.server.server import EvaServer
from eva.utils.generic_utils import remove_directory_contents
import uuid

from eva.utils.logging_manager import logger


class GlobalState:
    def __init__(self) -> None:
        self._server_table = {}

    def is_instialized(self, config_manager: ConfigurationManager):
        for server_id in state.server_table:
            # todo (gaurav) improve this verfication, we may want to include other
            # config values
            def _compare(a, b):
                return (
                    a["server"]["host"] == b["server"]["host"]
                    and a["server"]["port"] == b["server"]["port"]
                    and a["core"]["catalog_database_uri"]
                    == b["core"]["catalog_database_uri"]
                )

            if _compare(state.server_table[server_id]["config"], config_manager):
                return True
        return False

    def initialize(self, config_manager: ConfigurationManager):
        new_uuid = uuid.uuid4()
        mode = config_manager.get_value("core", "mode")
        host = config_manager.get_value("server", "host")
        port = config_manager.get_value("server", "port")
        from eva.udfs.udf_bootstrap_queries import init_builtin_udfs  # noqa: E402

        init_builtin_udfs(mode=mode)

        server = EvaServer()

        # Launch the server in a separate process
        command = [
            "python",
            "-c",
            f"from eva.server.server import EvaServer; import asyncio; server = EvaServer(); asyncio.run(server.start_eva_server({host}, {port}))",
        ]
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # Get the process ID (PID) of the started server
        server_pid = process.pid

        if server_pid is None:
            return False

        print(f"EVA server started at host {host} and port {port}")
        self._server_table[str(new_uuid)] = {
            "server": server,
            "config": config_manager,
            "PID": server_pid,
        }
        return True

    @property
    def server_table(self):
        return self._server_table


state = GlobalState()


def shutdown():
    for server_id in state.server_table:
        # stop the server
        server = state.server_table[server_id].server
        asyncio.run(server.stop_eva_server())

        # clear the associated data
        server_db = state.server_table[server_id]["config"]["core"][
            "catalog_database_uri"
        ]
        remove_directory_contents(server_db)


def get_running_servers():
    return state.server_table


async def _get_connection(host: str, port: int) -> EVAConnection:
    reader, writer = await asyncio.open_connection(host, port)
    connection = EVAConnection(reader, writer)
    return connection


def connect(
    db: str = "eva_data", host: str = "0.0.0.0", port: int = 8803
) -> EVAConnection:
    # Instantiate a Configuration Manager object with the appropriate database directory
    # Subsequent calls will utilize the specified database directory
    config_manager = ConfigurationManager(EVA_DATABASE_DIR=db)
    config_manager.update_value("server", "host", host)
    config_manager.update_value("server", "port", port)

    # start a new server if there isn't any running with the same config
    if not state.is_instialized(config_manager):
        if not state.initialize(config_manager):
            logger.error("Failed to start the server")
            return None

    connection = asyncio.run(_get_connection(host, port))
    return connection
