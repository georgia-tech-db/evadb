from ExpressionComparison import ExpressionComparison
from ExpressionConstant import ExpressionConstant
from ExpressionTuple import ExpressionTuple
from ExpressionLogical import ExpressionLogical
from ExpressionArithmetic import ExpressionArithmetic

data=[[0,50,'bus'],[1,100,'car'],[2,50,'van'],[3,150,'bus'],[4,120,'bus'],[5,130,'car'],[6,250,'bus'],[7,70,'van'],[8,110,'bus']]

for line in data:
    expression1=ExpressionTuple('REDNESS') #class
    expression2=ExpressionConstant('bus') #bus
    expression31=ExpressionTuple('CLASS')
    expression32=ExpressionConstant('30')
    expression3=ExpressionArithmetic([expression31,expression32],'-') #redness
    expression4=ExpressionConstant('100') #100
    expression5=ExpressionComparison([expression1,expression2],'=') #=
    expression6=ExpressionComparison([expression3,expression4],'>') #>
    expression7=ExpressionLogical([expression5,expression6],'AND') #AND
    print(expression7.evaluate(line))
