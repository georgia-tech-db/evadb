# import unittest
import sys, os
sys.path.append('../')
from src.query_parser.eva_parser import EvaFrameQLParser
# from src.query_parser.eva_statement import EvaStatement
# from src.query_parser.eva_statement import StatementType
# from src.query_parser.select_statement import SelectStatement
# from src.expression.abstract_expression import ExpressionType
# from src.query_parser.table_ref import TableRef

from cmd import Cmd

class EVADemo(Cmd):

    def default(self, args):
        """Takes in SQL query and generates the output"""

        # Type exit 
        if(args == "exit" or args == "EXIT"):
            raise SystemExit

        if len(args) == 0:
            
            query = 'Unknown'
        else:
            parser = EvaFrameQLParser()
            eva_statement = parser.parse(args)
            query = args
            # print(eva_statement)
            select_stmt = eva_statement[0]
            print("Result from the parser:")
            print(select_stmt)
            print('\n')
                    
        

    def do_quit(self, args):
        """Quits the program."""
        print ("Quitting.")
        raise SystemExit


if __name__ == '__main__': 
    prompt = EVADemo()
    prompt.prompt = '> '
    prompt.cmdloop('Starting EVA...')

