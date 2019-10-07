from query_optimizer.query_optimizer import QueryOptimizer

obj=QueryOptimizer()

def test_parseQuery():

    #case 1: Simple input/ouput check
    predicates,connectors=obj._parseQuery("t>60 && q>=4 && v=car")
    if predicates!=[["t",">","60"],["q",">=","4"],["v","=","car"]]:
        assert False,"Wrong breakdown of predicates"
    if connectors!=["&&","&&"]:
        assert False,"Wrong list of connectors"

    # case 2: Case when an extra space is present in the input
    predicates, connectors = obj._parseQuery("t>60  && q>=4 && v=car")
    if predicates != [["t", ">", "60"], ["q", ">=", "4"], ["v", "=", "car"]]:
        assert False, "Wrong breakdown of predicates, can't handle consecutive spaces."
    if connectors != ["&&", "&&"]:
        assert False, "Wrong list of connectors"

    #case 2: No operator exists
    predicates, connectors = obj._parseQuery("t!60")
    if predicates != []:
        assert False, "Wrong breakdown of predicates"
    if connectors != []:
        assert False, "Wrong list of connectors"

    predicates, connectors = obj._parseQuery("t>60 && adfsg")
    if predicates != []:
        assert False, "Wrong breakdown of predicates"
    if connectors != []:
        assert False, "Wrong list of connectors"

    #case for >> and similar situations, the >> operator should be recognised as >
    predicates, connectors = obj._parseQuery("t>>60 && a<45")
    print(predicates, connectors)
    if predicates != [['t','>','60'],['a','<','45']]:
        assert False, "Wrong breakdown of predicates,the >> operator should be recognised as > and likewise for <"
    if connectors != ['&&']:
        assert False, "Wrong list of connectors"

    #case 2: Check for ordering of execution based on parenthesis code does not handle this yet so now way to test at the moment
    predicates, connectors = obj._parseQuery("t>60||(q>=4&&v=car)")
    if predicates != [["t", ">", "60"], ["q", ">=", "4"], ["v", "=", "car"]]:
        assert False, "Wrong breakdown of predicates"
    if connectors != ["&&", "&&"]:
        assert False, "Wrong list of connectors"

    assert True

def test_convertL2S():
    query_string=obj.convertL2S(["t","!=","10"],[])
    if query_string!="t!=10":
        assert False,"Wrong output query string"
    assert True

    query_string = obj.convertL2S([["t", "!=", "10"],['a','<','5'],['b','=','1003']], ["&&","||"])
    if query_string != "t!=10 && a<5 || b=1003":
        assert False, "Wrong output query string"

    #case for paranthesis hasn't been implemented yet when its done need to add test cases for that.
    assert True

test_parseQuery()
test_convertL2S()