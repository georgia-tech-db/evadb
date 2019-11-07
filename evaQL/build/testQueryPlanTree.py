import sys
from antlr4 import *
from frameQLParser import frameQLParser 
from frameQLLexer import frameQLLexer
from frameQLParserListener import frameQLParserListener
from MyListener import MyListener
from Nodes.NodeProjection import NodeProjection
from Nodes.NodeCondition import NodeCondition
from Nodes.NodeCross import NodeCross


def main(argv):
    input_stream = FileStream(argv)
    lexer = frameQLLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = frameQLParser(stream)
    tree = parser.root()
    listener = MyListener()
    walker = ParseTreeWalker()
    walker.walk(listener,tree)

    PlanTree = listener.projectionNode
    print(PlanTree.attributes)
    print(PlanTree.children.expression)
    print(PlanTree.children.children.data)
    #print(tree.toStringTree(recog=parser))

if __name__ == '__main__':
    main('test3.txt')
