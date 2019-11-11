from query_optimizer.expr_parser import ExprParser, Grammar


def test_expression_parser():
    query = 't = van && s > 60.0 && o = pt211'
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
    assert str(output) == query