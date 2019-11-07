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
from Nodes.NodeJoin import NodeJoin

class MyListener(frameQLParserListener):
    def __init__(self):
        #Attributes
        self.listAttributes=['CLASS','REDNESS']
        
        #Build the query plan tree
        
        #We either use crossNode or joinNode
        self.joinNode=NodeJoin([],[])
        self.crossNode=NodeCross(None)
        
        self.projectionNode=NodeProjection(self.crossNode,None)
        self.conditionNode=None
        
        
        self.hasJoin=False
    
        #Build the expression tree
        self.currentComparisonExpression=None
        self.FIFO=[]

    #Build the expression tree
    def enterLogicalExpression(self, ctx:frameQLParser.LogicalExpressionContext):
        #Logical Tree
        if self.hasJoin==True:
            return None
        if self.conditionNode == None:
            self.conditionNode=NodeCondition(self.crossNode,None)
            self.projectionNode.children=self.conditionNode
            if len(self.joinNode.attributes)==0:
                self.conditionNode.children=self.crossNode
            else:
                self.conditionNode.children=self.joinNode

        #ExpressionTree
        self.FIFO.append(ExpressionLogical([],None))
    def exitLogicalExpression(self, ctx:frameQLParser.LogicalExpressionContext):
        #Logical Tree
        if self.hasJoin==True:
            return None

        #ExpressionTree
        if len(self.FIFO)>1:
            temp=self.FIFO.pop()
            self.FIFO[-1].children.append(temp)
        elif len(self.FIFO)==1:
            #Logical Tree
            self.conditionNode.expression=self.FIFO[0]
    def enterLogicalOperator(self, ctx:frameQLParser.LogicalOperatorContext):
        #ExpressionTree
        self.FIFO[-1].operator=ctx.getText()
    def enterPredicateExpression(self, ctx:frameQLParser.PredicateExpressionContext):
        #Logical Tree
        if self.hasJoin==True:
            return None
        #ExpressionTree
        if (len(ctx.getText().split('='))+len(ctx.getText().split('>'))+len(ctx.getText().split('<'))+len(ctx.getText().split('>='))+len(ctx.getText().split('<=')))==6:
            self.currentComparisonExpression=ExpressionComparison([None,None],None)
    def exitPredicateExpression(self, ctx:frameQLParser.PredicateExpressionContext):
        #Logical Tree
        if self.hasJoin==True:
            return None
        #ExpressionTree
        if (len(ctx.getText().split('='))+len(ctx.getText().split('>'))+len(ctx.getText().split('<'))+len(ctx.getText().split('>='))+len(ctx.getText().split('<=')))==6:
            self.FIFO[-1].children.append(self.currentComparisonExpression)
    def enterExpressionAtomPredicate(self, ctx:frameQLParser.ExpressionAtomPredicateContext):
        #Logical Tree
        if self.hasJoin==True:
            self.joinNode.attributes.append(ctx.getText())
            return None
        #ExpressionTree
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
        #Logical Tree
        if self.hasJoin==True:
            return None
        #ExpressionTree
        self.currentComparisonExpression.operator=ctx.getText()

    #Build the query plan tree
    def enterSelectElements(self, ctx:frameQLParser.SelectElementsContext):
        self.projectionNode.attributes=ctx.getText()
    
    def enterInnerJoin(self, ctx:frameQLParser.InnerJoinContext):
        self.hasJoin=True
        
    def exitInnerJoin(self, ctx:frameQLParser.InnerJoinContext):
        self.hasJoin=False


    def enterTableName(self, ctx:frameQLParser.TableNameContext):
        self.joinNode.data.append(ctx.getText())
        if self.hasJoin==False:
            self.crossNode.data=ctx.getText()
            
