from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
from query_optimizer.parse_ops import Attr, Expr, Literal, Paren


class ExprParser(NodeVisitor):

    def __init__(self):
        self.grammar =  Grammar(
                            r"""
                            exprstmt = ws expr ws
                            expr     = biexpr / unexpr / value
                            biexpr   = value ws binaryop ws expr
                            unexpr   = unaryop ws expr
                            value    = parenval / 
                                       number /
                                       boolean /
                                       NULL / 
                                       function /
                                       col_ref /
                                       string /
                                       attr
                            parenval = "(" ws expr ws ")"
                            function = fname "(" ws arg_list? ws ")"
                            arg_list = expr (ws "," ws expr)*
                            number   = ~"\d*\.?\d+"i
                            string   = ~"\'\w*\'"i
                            col_ref  = (name "." (name ".")? )? name
                            attr     = ~"\w[\w\d]*"i
                            name     = ~"[a-zA-Z]\w*"i
                            fname    = ~"\w[\w\d]*"i
                            boolean  = "true" / "false"
                            compound_op = "UNION" / "union"
                            binaryop = "+" / "-" / "*" / "/" / "=" / "<>" /
                                       "<=" / ">" / "<" / ">" / 
                                       "and" / "AND" / "or" / "OR" / 
                                       "&&" / "||" /
                                       "is" / "IS"
                            unaryop  = "+" / "-" / "not" / "NOT"
                            ws       = ~"\s*"i
                            wsp      = ~"\s+"i
                            NULL     = "null" / "NULL"
                            """)

    def visit_name(self, node, children):
        return node.text

    def visit_col_ref(self, node, children):
        attrname = children[-1]
        dbtable = children[0]
        db = table = None
        if dbtable and isinstance(dbtable, list):
            db, table = tuple(dbtable)
        elif isinstance(dbtable, str):
            table = dbtable
        return Attr(attrname, table, db)

    def visit_attr(self, node, children):
        return Attr(node.text)

    def visit_NULL(self, node, children):
        return "null"

    def visit_binaryop(self, node, children):
        return node.text

    def visit_biexpr(self, node, children):
        children = list(filter(bool, children))
        return Expr(children[1], children[0], children[-1])

    def visit_unaryop(self, node, children):
        return node.text.strip()

    def visit_unexpr(self, node, children):
        return Expr(children[0], children[-1])

    def visit_expr(self, node, children):
        return children[0]

    def visit_fname(self, node, children):
        return node.text

    def visit_arg_list(self, node, children):
        return flatten(children, 0, 1)

    def visit_number(self, node, children):
        return Literal(float(node.text))

    def visit_string(self, node, children):
        return Literal(node.text)

    def visit_parenval(self, node, children):
        return Paren(children[2])

    def visit_value(self, node, children):
        return children[0]

    def visit_boolean(self, node, children):
        if node.text == "true":
            return Literal(True)
        return Literal(False)

    def generic_visit(self, node, children):
        f = lambda v: v and (not isinstance(v, str) or v.strip())
        children = list(filter(f, children))
        if len(children) == 1:
            return children[0]
        return children


def parse(s):
  return ExprParser().parse(s)


if __name__ == '__main__':

    query = 't=van && s>60 && o=pt211'
    expr_parser = ExprParser()
    parsed = expr_parser.visit(query)
