"""
Sphinx directive for HTML Panel Box Components.
"""
from docutils import nodes
from docutils.parsers.rst import Directive, directives

from .utils import generate_template


class PanelBox(Directive):
    has_content = True
    option_spec = {
        "title": directives.unchanged_required,
        "class": directives.unchanged,
        "id": directives.unchanged,
    }

    def run(self):
        class_name = "panel"
        container_class_name = self.options.get("class", "")

        html0 = generate_template(
            """
            <div class="cell {container_class_name}">
                <div class="{class_name}">
                    <h5 class="{class_name}__title">{title}</h5>
            """,
            container_class_name=container_class_name,
            class_name=class_name,
            title=self.options.get("title", ""),
        )

        html1 = "</div></div>"

        description_node = nodes.container()
        if self.state:
            self.state.nested_parse(self.content, 0, description_node)

        return [
            nodes.raw(text=html0, format="html"),
            description_node,
            nodes.raw(text=html1, format="html"),
        ]


def setup(app):
    app.add_directive("panel-box", PanelBox)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
