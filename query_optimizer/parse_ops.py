from .expr_parser import parse


def _parse_expr(expr):
    if hasattr(expr, "__call__"):
        return expr
    if isinstance(expr, str):
        return parse(expr)
    raise Exception("Can't interpret as expression: %s" % expr)


class Operator(object):
    """
    Operator Base class.
    Creates tree structure.
    """

    def __init__(self):
        self.p = None

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, o):
        return o and hash(self) == hash(o)

    def replace(self, newop):
        """
        replace myself with @newop in the tree
        """
        if not self.p: return
        p = self.p
        if isinstance(p, UnaryOperator):
            p.c = newop
        if isinstance(p, BinaryOperator):
            if p.l == self:
                p.l = newop
            elif p.r == self:
                p.r = newop
        if isinstance(p, NaryOperator):
            if self in p.cs:
                cs[cs.index(self)] = newop
            p.cs = cs

    def is_ancestor(self, anc):
        """
        Check if @anc is an ancestor of the current operator
        """
        n = self
        seen = set()
        while n and n not in seen:
            seen.add(n)
            if n == anc:
                return True
            n = n.p
        return False

    def children(self):
        """
        Go through all attributes of this object and return those that
        are subclasses of Operator
        """
        children = []
        for key, attrval in self.__dict__.items():
            if key == "p":
                continue
            if not isinstance(attrval, list):
                attrval = [attrval]
            for v in attrval:
                if v and isinstance(v, Operator):
                    children.append(v)
        return children

    def traverse(self, f, path=None):
        """
        Visit each operator in the query plan, and call f()
        @f a functions that takes as input the current operator and
           the path to the operator
        """
        if path is None:
            path = []
        path = path + [self]
        f(self, path)
        for child in self.children():
            child.traverse(f, path)

    def is_type(self, klass_or_names):
        if not isinstance(klass_or_names, list):
            klass_or_names = [klass_or_names]
        names = [kn for kn in klass_or_names if isinstance(kn, str)]
        klasses = [kn for kn in klass_or_names if isinstance(kn, type)]
        return (self.__class__.__name__ in names or
                any([isinstance(self, kn) for kn in klasses]))

    def collect(self, klass_or_names):
        """
        Returns all operators in the subplan rooted at the current object
        that has the same class name, or is a subclass, as the arguments
        """
        ret = []
        if not isinstance(klass_or_names, list):
            klass_or_names = [klass_or_names]
        names = [kn for kn in klass_or_names if isinstance(kn, str)]
        klasses = [kn for kn in klass_or_names if isinstance(kn, type)]

        def f(node, path):
            if node and (
                    node.__class__.__name__ in names or
                    any([isinstance(node, kn) for kn in klasses])):
                ret.append(node)

        self.traverse(f)
        return ret

    def collectone(self, klassnames):
        """
        Helper function to return an arbitrary operator that matches any of the
        klass names or klass objects, or None
        """
        l = self.collect(klassnames)
        if l:
            return l[0]
        return None

    def to_str(self):
        """
        Return a description of the operator (ignoring children)
        """
        return ""

    def to_python(self):
        return self.to_str()

    def __str__(self):
        lines = []

        def f(op, path):
            if isinstance(op, ExprBase): return
            indent = "  " * (len(path) - 1)
            lines.append(indent + op.to_str())

        self.traverse(f)
        lines = filter(lambda l: l.strip(), lines)
        return "\n".join(lines)


class UnaryOperator(Operator):
    def __init__(self, c):
        super(UnaryOperator, self).__init__()
        self.c = c
        if c:
            c.p = self

    def __setattr__(self, attr, v):
        super(UnaryOperator, self).__setattr__(attr, v)
        if attr == "c" and v:
            self.c.p = self


class BinaryOperator(Operator):
    def __init__(self, l, r):
        super(BinaryOperator, self).__init__()
        self.l = l
        self.r = r
        if l:
            l.p = self
        if r:
            r.p = self

    def __setattr__(self, attr, v):
        super(BinaryOperator, self).__setattr__(attr, v)
        if attr in ("l", "r") and v:
            v.p = self


class NaryOperator(Operator):
    def __init__(self, cs):
        super(NaryOperator, self).__init__()
        self.cs = cs
        for c in cs:
            if c:
                c.p = self

    def __setattr__(self, attr, v):
        super(NaryOperator, self).__setattr__(attr, v)
        if attr == "cs":
            for c in self.cs:
                c.p = self

class Print(UnaryOperator):
    def __iter__(self):
        for row in self.c:
            print(row)
        yield

    def to_str(self):
        return "Print()"


def unary(op, v):
    """
    interpretor for executing unary operator expressions
    """
    if op == "+":
        return v
    if op == "-":
        return -v
    if op.lower() == "not":
        return not (v)


def binary(op, l, r):
    """
    interpretor for executing binary operator expressions
    """
    if op == "+": return l + r
    if op == "/": return l / r
    if op == "*": return l * r
    if op == "-": return l - r
    if op == "=": return l == r
    if op == "==": return l == r
    if op == "<>": return l != r
    if op == "!=": return l != r
    if op == "and": return l and r
    if op == "or": return l or r
    if op == "<": return l < r
    if op == ">": return l > r
    if op == "<=": return l <= r
    if op == ">=": return l >= r
    return True


class ExprBase(Operator):
    def __str__(self):
        return self.to_str()


class Expr(ExprBase):
    def __init__(self, op, l, r=None):
        self.op = op
        self.l = l
        self.r = r

    def to_str(self):
        if self.r is not None:
            return "%s %s %s" % (self.l, self.op, self.r)
        return "%s %s" % (self.op, self.l)

    def to_python(self):
        op = self.op
        if op == "=": op = "=="
        if self.r:
            return "%s %s %s" % (self.l.to_python(), op, self.r.to_python())
        return "%s %s" % (self.op, self.r.to_python())

    def __call__(self, tup, tup2=None):
        l = self.l(tup, tup2)
        if self.r is None:
            return unary(self.op, l)
        r = self.r(tup, tup2)
        return binary(self.op, l, r)


class Paren(UnaryOperator, ExprBase):
    def to_str(self):
        return "(%s)" % self.c

    def __call__(self, tup, tup2=None):
        return self.c(tup)

class Literal(ExprBase):
    def __init__(self, v):
        self.v = v

    def __call__(self, tup=None, tup2=None):
        return self.v

    def to_str(self):
        if isinstance(self.v, str):
            return "'%s'" % self.v
        return str(self.v)


class Bool(ExprBase):
    def __init__(self, v):
        self.v = v

    def __call__(self, *args, **kwargs):
        return self.v

    def to_str(self):
        return str(self.v)


class Attr(ExprBase):
    def __init__(self, attr, tablename=None, dbname=None):
        self.attr = attr
        self.tablename = tablename
        self.dbname = dbname
        if self.tablename:
            print("WARNING: can't deal with * for specific tables: %s" % self.tablename)
        if self.dbname:
            print("WARNING: can't deal with * for specific databases: %s" % self.dbname)

    def __call__(self, tup, tup2=None):
        if self.attr in tup:
            return tup[self.attr]
        if tup2 and self.attr in tup2:
            return tup2[self.attr]
        raise Exception("couldn't find %s in either tuple" % self.attr)

    def to_str(self):
        vals = [self.dbname, self.tablename, self.attr]
        return ".".join(filter(bool, vals))

    def to_python(self):
        return """%s["%s"]""" % (self.tablename, self.attr)


if __name__ == '__main__':
    pass
