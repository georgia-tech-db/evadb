from src.query_parser.select_statement import SelectStatement

class Statement2Plantree:
    def __init__(self):
        pass

    @staticmethod
    def convert(statement_list):
        if len(statement_list) > 1:
            print('nested queries are not handled yet')
        else:
            statement = statement_list[0]
            



