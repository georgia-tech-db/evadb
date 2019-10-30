from antlr4 import *
if __name__ is not None and "." in __name__:
    from .frameQLParser import frameQLParser
else:
    from frameQLParser import frameQLParser
from frameQLParserListener import frameQLParserListener

from Expressions.ExpressionComparison import ExpressionComparison
from Expressions.ExpressionLogical import ExpressionLogical
from Expressions.ExpressionTuple import ExpressionTuple
from Expressions.ExpressionConstant import ExpressionConstant

from Nodes.NodeCondition import NodeCondition
from Nodes.NodeCross import NodeCross
from Nodes.NodeProjection import NodeProjection

class MyListener(frameQLParserListener):
    def __init__(self):
        #Attributes
        self.listAttributes=['CLASS','REDNESS']
        
        #Build the query plan tree
        self.crossNode=NodeCross(None)
        self.conditionNode=NodeCondition(self.crossNode,None)
        self.projectionNode=NodeProjection(self.conditionNode,None)
    
        #Build the expression tree
        self.currentComparisonExpression=None
        self.FIFO=[]
 
    #Build the expression tree
    def enterLogicalExpression(self, ctx:frameQLParser.LogicalExpressionContext):
        self.FIFO.append(ExpressionLogical([],None))
    def exitLogicalExpression(self, ctx:frameQLParser.LogicalExpressionContext):
        if len(self.FIFO)>1:
            temp=self.FIFO.pop()
            self.FIFO[-1].children.append(temp)
        elif len(self.FIFO)==1:
            self.conditionNode.expression=self.FIFO[0]
    def enterLogicalOperator(self, ctx:frameQLParser.LogicalOperatorContext):
        self.FIFO[-1].operator=ctx.getText()
        
    def enterPredicateExpression(self, ctx:frameQLParser.PredicateExpressionContext):
        if len(ctx.getText().split('AND'))>1 or len(ctx.getText().split('OR'))>1:
            pass
        else:
            self.currentComparisonExpression=ExpressionComparison([None,None],None)
    def exitPredicateExpression(self, ctx:frameQLParser.PredicateExpressionContext):
        if len(ctx.getText().split('AND'))>1 or len(ctx.getText().split('OR'))>1:
            pass
        else:
            self.FIFO[-1].children.append(self.currentComparisonExpression)
    def enterExpressionAtomPredicate(self, ctx:frameQLParser.ExpressionAtomPredicateContext):
        if len(ctx.getText().split('AND'))>1 or len(ctx.getText().split('OR'))>1:
            pass
        elif self.currentComparisonExpression.children[0]==None:
            if ctx.getText() in self.listAttributes:
                self.currentComparisonExpression.children[0]=ExpressionTuple(ctx.getText())
            else:
                self.currentComparisonExpression.children[0]=ExpressionConstant(ctx.getText())
        elif self.currentComparisonExpression.children[0]!=None and self.currentComparisonExpression.children[1]==None:
            if ctx.getText() in self.listAttributes:
                self.currentComparisonExpression.children[1]=ExpressionTuple(ctx.getText())
            else:
                self.currentComparisonExpression.children[1]=ExpressionConstant(ctx.getText())
    def enterComparisonOperator(self, ctx:frameQLParser.ComparisonOperatorContext):
        self.currentComparisonExpression.operator=ctx.getText()

    #Build the query plan tree
    def enterSelectElements(self, ctx:frameQLParser.SelectElementsContext):
        self.projectionNode.attributes=ctx.getText()
    def enterTableSources(self, ctx:frameQLParser.TableSourcesContext):
        self.crossNode.data=ctx.getText()
