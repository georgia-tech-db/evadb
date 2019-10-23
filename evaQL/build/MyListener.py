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
        self.currentLogicalExpression=None
        self.rootExpression=None
        
    def enterLogicalOperator(self, ctx:frameQLParser.LogicalOperatorContext):
        self.currentLogicalExpression.operator=ctx.getText()

    def enterComparisonOperator(self, ctx:frameQLParser.ComparisonOperatorContext):
        self.currentComparisonExpression.operator=ctx.getText()
        
    def enterExpressionAtomPredicate(self, ctx:frameQLParser.ExpressionAtomPredicateContext):
        if self.currentComparisonExpression.children[0]==None:
            if ctx.getText() in self.listAttributes:
                self.currentComparisonExpression.children[0]=ExpressionTuple(ctx.getText())
            else:
                self.currentComparisonExpression.children[0]=ExpressionConstant(ctx.getText())
        elif self.currentComparisonExpression.children[0]!=None and self.currentComparisonExpression.children[1]==None:
            if ctx.getText() in self.listAttributes:
                self.currentComparisonExpression.children[1]=ExpressionTuple(ctx.getText())
            else:
                self.currentComparisonExpression.children[1]=ExpressionConstant(ctx.getText())
    def enterSelectElements(self, ctx:frameQLParser.SelectElementsContext):
        self.projectionNode.attributes=ctx.getText()
        
    def enterTableSources(self, ctx:frameQLParser.TableSourcesContext):
        self.crossNode.data=ctx.getText()

    def enterPredicateExpression(self, ctx:frameQLParser.PredicateExpressionContext):
        self.currentComparisonExpression=ExpressionComparison([None,None],None)
    def exitPredicateExpression(self, ctx:frameQLParser.PredicateExpressionContext):
        if self.currentLogicalExpression.children[0]==None:
            self.currentLogicalExpression.children[0]=self.currentComparisonExpression
        elif self.currentLogicalExpression.children[0]!=None and self.currentLogicalExpression.children[1]==None:
            self.currentLogicalExpression.children[1]=self.currentComparisonExpression
    def enterLogicalExpression(self, ctx:frameQLParser.LogicalExpressionContext):
        self.currentLogicalExpression=ExpressionLogical([None,None],None)

    def exitLogicalExpression(self, ctx:frameQLParser.LogicalExpressionContext):
        self.conditionNode.expression=self.currentLogicalExpression
        self.conditionNode.children=self.crossNode
