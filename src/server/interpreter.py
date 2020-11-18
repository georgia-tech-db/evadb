from cmd import Cmd
from contextlib import ExitStack
from src.server.eva_db_api import connect
from src.models.server.response import Response

from src.utils.logging_manager import LoggingManager


class EvaCommandInterpreter(Cmd):

    def __init__(self):
        super().__init__()

    def set_protocol(self, protocol):
        self._protocol = protocol

    def do_greet(self, line):
        print("greeting %s" % line)

    def set_connection(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor()

    def emptyline(self):
        print("Enter a valid query.")
        return False

    def do_quit(self, args):
        """Quits the program."""
        return True

    def do_exit(self, args):
        """Quits the program."""
        return True

    def default(self, line):
        """Considers the input as a query"""
        return self.do_query(line)

    def do_query(self, query):
        """Takes in SQL query and generates the output"""

        self.cursor.execute(query)
        print(self.cursor.fetch_all())

        return False

def handle_user_input(connection):
    """
        Reads from stdin in separate thread

        If user inputs 'quit' stops the event loop
        otherwise just echoes user input
    """

    # Start command interpreter
    prompt = EvaCommandInterpreter()
    prompt.prompt = '$ '

    prompt.set_connection(connection)

    prompt.cmdloop('Welcome to EVA Server')


def start_client(host: str, port: int):
    """
        Wait for the connection to open and the task to be processed.

        - There's retry logic to make sure we're connecting even in
          the face of momentary ECONNRESET on the server-side.
        - Socket will be automatically closed by the exit stack.
    """

    with ExitStack() as stack:
        connection = connect(host, port)
        handle_user_input(connection)
