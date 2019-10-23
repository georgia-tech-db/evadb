import sys
from antlr4 import *
from frameQLParser import frameQLParser 
from frameQLLexer import frameQLLexer
from frameQLParserListener import frameQLParserListener
from MyListener import MyListener
from Nodes.NodeProjection import NodeProjection
from Nodes.NodeCondition import NodeCondition
from Nodes.NodeCross import NodeCross

#convert the query so that frameQLLexer can read it
def convert_query(query):
    new_query=query.split(' FROM')[0]+'\r\nFROM'+query.split('FROM')[1]
    new_query=new_query.split(' WHERE')[0]+'\r\nWHERE'+new_query.split('WHERE')[1]
    new_query=new_query+'\r\n'
    return new_query

def main(argv):
    input_stream = FileStream(argv)
    #query=convert_query('SELECT CLASS , REDNESS FROM TAIPAI WHERE CLASS = \'BUS\' AND REDNESS > 200')
    #input_stream.strdata=query
    lexer = frameQLLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = frameQLParser(stream)
    tree = parser.root()
    listener = MyListener()
    walker = ParseTreeWalker()
    walker.walk(listener,tree)
    
    print(tree.toStringTree(recog=parser))
    
    ExpressionTree=listener.currentLogicalExpression
    PlanTree=listener.projectionNode

    print(ExpressionTree.children[0].children[0].attribute)
    print(ExpressionTree.children[0].operator)
    print(ExpressionTree.children[0].children[1].data)
    print(ExpressionTree.children[1].children[0].attribute)
    print(ExpressionTree.children[1].operator)
    print(ExpressionTree.children[1].children[1].data)
 
if __name__ == '__main__':
    main('test.txt')
