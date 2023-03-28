# updated SQLA schema display to work with pydot 1.0.2

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager
from sqlalchemy.orm.properties import RelationshipProperty
import pydot
import types

__all__ = [
    "create_uml_graph",
    "create_schema_graph",
    "show_uml_graph",
    "show_schema_graph",
]


def _mk_label(
    mapper, show_operations, show_attributes, show_datatypes, show_inherited, bordersize
):
    html = (
        '<<TABLE CELLSPACING="0" CELLPADDING="1" BORDER="0" CELLBORDER="%d" ALIGN="LEFT"><TR><TD><FONT POINT-SIZE="10">%s</FONT></TD></TR>'
        % (bordersize, mapper.class_.__name__)
    )

    def format_col(col):
        colstr = "+%s" % (col.name)
        if show_datatypes:
            colstr += " : %s" % (col.type.__class__.__name__)
        return colstr

    if show_attributes:
        if not show_inherited:
            cols = [c for c in mapper.columns if c.table == mapper.tables[0]]
        else:
            cols = mapper.columns
        html += '<TR><TD ALIGN="LEFT">%s</TD></TR>' % '<BR ALIGN="LEFT"/>'.join(
            format_col(col) for col in cols
        )
    else:
        [
            format_col(col)
            for col in sorted(mapper.columns, key=lambda col: not col.primary_key)
        ]
    if show_operations:
        html += '<TR><TD ALIGN="LEFT">%s</TD></TR>' % '<BR ALIGN="LEFT"/>'.join(
            "%s(%s)"
            % (
                name,
                ", ".join(
                    default is _mk_label
                    and ("%s") % arg
                    or ("%s=%s" % (arg, repr(default)))
                    for default, arg in zip(
                        (
                            func.func_defaults
                            and len(func.func_code.co_varnames)
                            - 1
                            - (len(func.func_defaults) or 0)
                            or func.func_code.co_argcount - 1
                        )
                        * [_mk_label]
                        + list(func.func_defaults or []),
                        func.func_code.co_varnames[1:],
                    )
                ),
            )
            for name, func in mapper.class_.__dict__.items()
            if isinstance(func, types.FunctionType)
            and func.__module__ == mapper.class_.__module__
        )
    html += "</TABLE>>"
    return html


def escape(name):
    return '"%s"' % name


def create_uml_graph(
    mappers,
    show_operations=True,
    show_attributes=True,
    show_inherited=True,
    show_multiplicity_one=False,
    show_datatypes=True,
    linewidth=1.0,
    font="Bitstream-Vera Sans",
):
    graph = pydot.Dot(
        prog="neato",
        mode="major",
        overlap="0",
        sep="0.01",
        dim="3",
        pack="True",
        ratio=".75",
    )
    relations = set()
    for mapper in mappers:
        graph.add_node(
            pydot.Node(
                escape(mapper.class_.__name__),
                shape="plaintext",
                label=_mk_label(
                    mapper,
                    show_operations,
                    show_attributes,
                    show_datatypes,
                    show_inherited,
                    linewidth,
                ),
                fontname=font,
                fontsize="8.0",
            )
        )
        if mapper.inherits:
            graph.add_edge(
                pydot.Edge(
                    escape(mapper.inherits.class_.__name__),
                    escape(mapper.class_.__name__),
                    arrowhead="none",
                    arrowtail="empty",
                    style="setlinewidth(%s)" % linewidth,
                    arrowsize=str(linewidth),
                )
            )
        for loader in mapper.iterate_properties:
            if isinstance(loader, RelationshipProperty) and loader.mapper in mappers:
                if hasattr(loader, "reverse_property"):
                    relations.add(frozenset([loader, loader.reverse_property]))
                else:
                    relations.add(frozenset([loader]))

    for relation in relations:
        # if len(loaders) > 2:
        #    raise Exception("Warning: too many loaders for join %s" % join)
        args = {}

        def multiplicity_indicator(prop):
            if prop.uselist:
                return " *"
            if hasattr(prop, "local_side"):
                cols = prop.local_side
            else:
                cols = prop.local_columns
            if any(col.nullable for col in cols):
                return " 0..1"
            if show_multiplicity_one:
                return " 1"
            return ""

        if len(relation) == 2:
            src, dest = relation
            from_name = escape(src.parent.class_.__name__)
            to_name = escape(dest.parent.class_.__name__)

            def calc_label(src, dest):
                return "+" + src.key + multiplicity_indicator(src)

            args["headlabel"] = calc_label(src, dest)

            args["taillabel"] = calc_label(dest, src)
            args["arrowtail"] = "none"
            args["arrowhead"] = "none"
            args["constraint"] = False
        else:
            (prop,) = relation
            from_name = escape(prop.parent.class_.__name__)
            to_name = escape(prop.mapper.class_.__name__)
            args["headlabel"] = "+%s%s" % (prop.key, multiplicity_indicator(prop))
            args["arrowtail"] = "none"
            args["arrowhead"] = "vee"

        graph.add_edge(
            pydot.Edge(
                from_name,
                to_name,
                fontname=font,
                fontsize="7.0",
                style="setlinewidth(%s)" % linewidth,
                arrowsize=str(linewidth),
                **args
            )
        )

    return graph


from sqlalchemy.dialects.postgresql.base import PGDialect
from sqlalchemy import MetaData, Table, text, ForeignKeyConstraint


def _render_table_html(
    table,
    metadata,
    show_indexes,
    show_datatypes,
    show_column_keys,
    show_schema_name,
    format_schema_name,
    format_table_name,
):
    # add in (PK) OR (FK) suffixes to column names that are considered to be primary key or foreign key
    use_column_key_attr = hasattr(
        ForeignKeyConstraint, "column_keys"
    )  # sqlalchemy > 1.0 uses column_keys to return list of strings for foreign keys, previously was columns
    if show_column_keys:
        if use_column_key_attr:
            # sqlalchemy > 1.0
            fk_col_names = set(
                [h for f in table.foreign_key_constraints for h in f.columns.keys()]
            )
        else:
            # sqlalchemy pre 1.0?
            fk_col_names = set(
                [h.name for f in table.foreign_keys for h in f.constraint.columns]
            )
        # fk_col_names = set([h for f in table.foreign_key_constraints for h in f.columns.keys()])
        pk_col_names = set([f for f in table.primary_key.columns.keys()])
    else:
        fk_col_names = set()
        pk_col_names = set()

    def format_col_type(col):
        try:
            return col.type.get_col_spec()
        except (AttributeError, NotImplementedError):
            return str(col.type)

    def format_col_str(col):
        # add in (PK) OR (FK) suffixes to column names that are considered to be primary key or foreign key
        suffix = (
            "(FK)"
            if col.name in fk_col_names
            else "(PK)"
            if col.name in pk_col_names
            else ""
        )
        if show_datatypes:
            return "- %s : %s" % (col.name + suffix, format_col_type(col))
        else:
            return "- %s" % (col.name + suffix)

    def format_name(obj_name, format_dict):
        # Check if format_dict was provided
        if format_dict is not None:
            # Should color be checked? Could use  /^#([A-Fa-f0-9]{8}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/
            return '<FONT COLOR="{color}" POINT-SIZE="{size}">{bld}{it}{name}{e_it}{e_bld}</FONT>'.format(
                name=obj_name,
                color=format_dict.get("color") if "color" in format_dict else "initial",
                size=float(format_dict["fontsize"])
                if "fontsize" in format_dict
                else "initial",
                it="<I>" if format_dict.get("italics") else "",
                e_it="</I>" if format_dict.get("italics") else "",
                bld="<B>" if format_dict.get("bold") else "",
                e_bld="</B>" if format_dict.get("bold") else "",
            )
        else:
            return obj_name

    schema_str = ""
    if (
        show_schema_name == True
        and hasattr(table, "schema")
        and table.schema is not None
    ):
        # Build string for schema name, empty if show_schema_name is False
        schema_str = format_name(table.schema, format_schema_name)
    table_str = format_name(table.name, format_table_name)

    # Assemble table header
    html = (
        '<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0"><TR><TD ALIGN="CENTER">%s%s%s</TD></TR><TR><TD BORDER="1" CELLPADDING="0"></TD></TR>'
        % (schema_str, "." if show_schema_name else "", table_str)
    )

    html += "".join(
        '<TR><TD ALIGN="LEFT" PORT="%s">%s</TD></TR>' % (col.name, format_col_str(col))
        for col in table.columns
    )
    if metadata.bind and isinstance(metadata.bind.dialect, PGDialect):
        # postgres engine doesn't reflect indexes
        indexes = dict(
            (name, defin)
            for name, defin in metadata.bind.execute(
                text(
                    "SELECT indexname, indexdef FROM pg_indexes WHERE tablename = '%s'"
                    % table.name
                )
            )
        )
        if indexes and show_indexes:
            html += '<TR><TD BORDER="1" CELLPADDING="0"></TD></TR>'
            for index, defin in indexes.items():
                ilabel = "UNIQUE" in defin and "UNIQUE " or "INDEX "
                ilabel += defin[defin.index("(") :]
                html += '<TR><TD ALIGN="LEFT">%s</TD></TR>' % ilabel
    html += "</TABLE>>"
    return html


def create_schema_graph(
    tables=None,
    metadata=None,
    show_indexes=True,
    show_datatypes=True,
    font="Bitstream-Vera Sans",
    concentrate=True,
    relation_options={},
    rankdir="TB",
    show_column_keys=False,
    restrict_tables=None,
    show_schema_name=False,
    format_schema_name=None,
    format_table_name=None,
):
    """
    Args:
      - metadata (sqlalchemy.MetaData, default=None): SqlAlchemy `MetaData` with reference to related tables.  If none
        is provided, uses metadata from first entry of `tables` argument.
      - concentrate (bool, default=True): Specifies if multiedges should be merged into a single edge & partially
        parallel edges to share overlapping path.  Passed to `pydot.Dot` object.
      - relation_options (dict, default: None): kwargs passed to pydot.Edge init.  Most attributes in
        pydot.EDGE_ATTRIBUTES are viable options.  A few values are set programmatically.
      - rankdir (string, default='TB'): Sets direction of graph layout.  Passed to `pydot.Dot` object.  Options are
        'TB' (top to bottom), 'BT' (bottom to top), 'LR' (left to right), 'RL' (right to left).
      - show_column_keys (bool, default=False): If true then add a PK/FK suffix to columns names that are primary and
        foreign keys.
      - restrict_tables (None or list of strings): Restrict the graph to only consider tables whose name are defined
        `restrict_tables`.
      - show_schema_name (bool, default=False): If true, then prepend '<schema name>.' to the table name resulting in
        '<schema name>.<table name>'.
      - format_schema_name (dict, default=None): If provided, allowed keys include: 'color' (hex color code incl #),
        'fontsize' as a float, and 'bold' and 'italics' as bools.
      - format_table_name (dict, default=None): If provided, allowed keys include: 'color' (hex color code incl #),
        'fontsize' as a float, and 'bold' and 'italics' as bools.
    """

    relation_kwargs = {"fontsize": "7.0", "dir": "both"}
    relation_kwargs.update(relation_options)

    if metadata is None and tables is not None and len(tables):
        metadata = tables[0].metadata
    elif tables is None and metadata is not None:
        if not len(metadata.tables):
            metadata.reflect()
        tables = metadata.tables.values()
    else:
        raise ValueError("You need to specify at least tables or metadata")

    # check if unexpected keys were used in format_schema_name param
    if (
        format_schema_name is not None
        and len(
            set(format_schema_name.keys()).difference(
                {"color", "fontsize", "italics", "bold"}
            )
        )
        > 0
    ):
        raise KeyError(
            "Unrecognized keys were used in dict provided for `format_schema_name` parameter"
        )
    # check if unexpected keys were used in format_table_name param
    if (
        format_table_name is not None
        and len(
            set(format_table_name.keys()).difference(
                {"color", "fontsize", "italics", "bold"}
            )
        )
        > 0
    ):
        raise KeyError(
            "Unrecognized keys were used in dict provided for `format_table_name` parameter"
        )

    graph = pydot.Dot(
        prog="dot",
        mode="ipsep",
        overlap="ipsep",
        sep="0.01",
        concentrate=str(concentrate),
        rankdir=rankdir,
    )
    if restrict_tables is None:
        restrict_tables = set([t.name.lower() for t in tables])
    else:
        restrict_tables = set([t.lower() for t in restrict_tables])
    tables = [t for t in tables if t.name.lower() in restrict_tables]
    for table in tables:
        graph.add_node(
            pydot.Node(
                str(table.name),
                shape="plaintext",
                label=_render_table_html(
                    table,
                    metadata,
                    show_indexes,
                    show_datatypes,
                    show_column_keys,
                    show_schema_name,
                    format_schema_name,
                    format_table_name,
                ),
                fontname=font,
                fontsize="7.0",
            )
        )

    for table in tables:
        for fk in table.foreign_keys:
            if fk.column.table not in tables:
                continue
            edge = [table.name, fk.column.table.name]
            is_inheritance = fk.parent.primary_key and fk.column.primary_key
            if is_inheritance:
                edge = edge[::-1]
            graph_edge = pydot.Edge(
                headlabel="+ %s" % fk.column.name,
                taillabel="+ %s" % fk.parent.name,
                arrowhead=is_inheritance and "none" or "odot",
                arrowtail=(fk.parent.primary_key or fk.parent.unique)
                and "empty"
                or "crow",
                fontname=font,
                # samehead=fk.column.name, sametail=fk.parent.name,
                *edge,
                **relation_kwargs
            )
            graph.add_edge(graph_edge)

    # not sure what this part is for, doesn't work with pydot 1.0.2
    #            graph_edge.parent_graph = graph.parent_graph
    #            if table.name not in [e.get_source() for e in graph.get_edge_list()]:
    #                graph.edge_src_list.append(table.name)
    #            if fk.column.table.name not in graph.edge_dst_list:
    #                graph.edge_dst_list.append(fk.column.table.name)
    #            graph.sorted_graph_elements.append(graph_edge)
    return graph


def show_uml_graph(*args, **kwargs):
    from cStringIO import StringIO
    from PIL import Image

    iostream = StringIO(create_uml_graph(*args, **kwargs).create_png())
    Image.open(iostream).show(command=kwargs.get("command", "gwenview"))


def show_schema_graph(*args, **kwargs):
    from cStringIO import StringIO
    from PIL import Image

    iostream = StringIO(create_schema_graph(*args, **kwargs).create_png())
    Image.open(iostream).show(command=kwargs.get("command", "gwenview"))


##########################################################################
##########################################################################
#########################################################################
# ###########################################################################

db_uri = ConfigurationManager().get_value("core", "catalog_database_uri")
catalog = CatalogManager()
restrict_tables = [
    "column_catalog",
    "table_catalog",
    "depend_column_and_udf_cache",
    "udf_cache",
    "udf_catalog",
    "depend_udf_and_udf_cache",
    "index_catalog",
    "udfio_catalog",
    "udf_cost_catalog",
    "udf_metadata_catalog",
]
graph = create_schema_graph(
    metadata=MetaData(db_uri),
    concentrate=True,
    rankdir="TD",
    font="trebuchet ms",
    show_column_keys=True,
    restrict_tables=restrict_tables,
    format_table_name={"bold": True, "fontsize": 10.0},
)
graph.write_png("docs/images/reference/catalog.png")
