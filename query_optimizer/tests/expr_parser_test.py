from query_optimizer.expr_parser import ExprParser, Grammar

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


def test_expression_parser():
    query = 't = van && s > 60.0 && o = pt211'
    tree = grammer.parse(query)
    iv = ExprParser()
    output = iv.visit(tree)
    assert str(output) == query


def test_basic_number_expression():
    query = 's > 60.0'
    tree = grammer.parse(query)
    iv = ExprParser()
    output = iv.visit(tree)
    assert str(output) == query


def test_basic_string_expression():
    query = 't = van'
    tree = grammer.parse(query)
    iv = ExprParser()
    output = iv.visit(tree)
    assert str(output) == query


def test_multiple_string_expression():
    query = 't = van && t = car || t = flight'
    tree = grammer.parse(query)
    iv = ExprParser()
    output = iv.visit(tree)
    assert str(output) == query


def test_multiple_number_expression():
    query = 's < 0.0 || s > 10.0 && s = 1.0'
    tree = grammer.parse(query)
    iv = ExprParser()
    output = iv.visit(tree)
    assert str(output) == query


def test_invalid_parser_expression():
    try:
        query = 's == 1.0'
        tree = grammer.parse(query)
        iv = ExprParser()
        output = iv.visit(tree)
        assert False, "Should fail, please check grammer"
    except:
        assert True, "Parsing error success"
