from parse_ops import Attr, Expr, Literal, Paren
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor


class ExprParser(NodeVisitor):

    def __init__(self):
        """
            Expression Parser uses parsimonius but specifying the grammer to it.
            We specify the grammer which is used to construct a query.
        """
        self.grammar = Grammar(
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
        """
        Returns the query present in the node.
        :param node: A node in the Expression parser.
        :return: Query present in the node.
        """
        return node.text

    def visit_col_ref(self, node, children):
        """
        Returns an object reference of the node and it children.
        :param node: A node in the Expression parser.
        :param children: child node(s) in the Expression parser.
        :return: object reference of the type of the node and it children.
        """
        attrname = children[-1]
        dbtable = children[0]
        db = table = None
        if dbtable and isinstance(dbtable, list):
            db, table = tuple(dbtable)
        elif isinstance(dbtable, str):
            table = dbtable
        return Attr(attrname, table, db)

    def visit_attr(self, node, children):
        """
            Returns the attribute object of node.
        :param node: A node in the Expression parser.
        :return: The attribute object of node.
        """
        return Attr(node.text)

    def visit_NULL(self):
        """
            Always return NULL
        :return: NULL
        """
        return "null"

    def visit_binaryop(self, node, children):
        """
            Function to visit binary operation
            :param node: A node in the Expression parser.
        """
        return node.text

    def visit_biexpr(self, node, children):
        """
            Returns a parsed binary expression
        :param node: A node in the Expression parser.
        :param children: A child node(s) in the Expression parser.
        :return: Parsed binary expression
        """
        children = list(filter(bool, children))
        return Expr(children[1], children[0], children[-1])

    def visit_unaryop(self, node):
        """
            Function to visit unary operation
            :param node: A node in the Expression parser.
        """
        return node.text.strip()

    def visit_unexpr(self, node, children):
        """
            Returns a unary expression of the child node(s).
        :param children: Child node(s) in the Expression parser.
        :return: a unary expression of the child node(s).
        """
        return Expr(children[0], children[-1])

    def visit_expr(self, node, children):
        """
            Function to visit first child.
        :param children: Child node(s) in the Expression parser.
        :return: first child
        """
        return children[0]

    def visit_fname(self, node, children):
        """
            Function to display function name of present node.
        :param node: A node of Expression tree
        :return: function name of node.
        """
        return node.text

    def visit_arg_list(self, node, children):
        """
            Flatten the supplied node and it's childs.
        :param children: A tree of child node(s).
        :return: Flatten the supplied node and it's childs.
        """
        return flatten(children, 0, 1)

    def visit_number(self, node, children):
        """
            Return a floating object literal of the node.
        :param node: A node of Expression tree
        :return: a floating object literal of the node.
        """
        return Literal(float(node.text))

    def visit_string(self, node, children):
        """
            Return a string object of the node's text.
        :param node: A node of Expression tree
        :return: a string object of the node's text.
        """
        return Literal(node.text)

    def visit_parenval(self, node, children):
        """
            Returns parent node object of children.
        :param children: List of child node(s).
        :return:
        """
        return Paren(children[2])

    def visit_value(self, node, children):
        """
            Returns value of node
        :param node: A node of Expression tree
        :return: Returns value of the node
        """
        return children[0]

    def visit_boolean(self, node, children):
        """
            Return the result of visiting a boolean node.
        :param node: A node of Expression tree
        :return: Either True or False Literal object
        """
        if node.text == "true":
            return Literal(True)
        return Literal(False)

    def generic_visit(self, node, children):
        """
            A generic visit node function to parse and return the node and it's children.
        :param node: A node of Expression tree
        :param children: Child Node(s) of the vising tree.
        :return:
        """
        f = lambda v: v and (not isinstance(v, str) or v.strip())
        children = list(filter(f, children))
        if len(children) == 1:
            return children[0]
        return children


def parse(s):
    return ExprParser().parse(s)


def _parse_expr(expr):
    if hasattr(expr, "__call__"):
        return expr
    if isinstance(expr, str):
        return parse(expr)
    raise Exception("Can't interpret as expression: %s" % expr)


if __name__ == '__main__':
    query = 't=van && s>60 && o=pt211'
    grammer = Grammar(
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
    tree = grammer.parse(query)
    iv = ExprParser()
    output = iv.visit(tree)
    print(output)
